#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from uuid import uuid4
from datetime import datetime, timedelta

from ujson import dumps
from colorama import Fore, Style
from octopus import TornadoOctopus
from octopus.limiter.redis.per_domain import Limiter
from retools.lock import Lock, LockTimeout
from sqlalchemy.orm import scoped_session

from holmes import __version__
from holmes.reviewer import Reviewer
from holmes.utils import load_classes, count_url_levels, get_domain_from_url
from holmes.models import Request, Key, DomainsViolationsPrefs
from holmes.cli import BaseCLI


class BaseWorker(BaseCLI):
    def _load_validators(self):
        return load_classes(default=self.config.VALIDATORS)

    def _load_facters(self):
        return load_classes(default=self.config.FACTERS)

    def get_otto_limiter(self):
        domains = self.cache.get_domain_limiters()
        limiter = None

        if domains:
            limiter = Limiter(
                *domains,
                redis=self.redis,
                expiration_in_seconds=self.config.LIMITER_LOCKS_EXPIRATION
            )

            limiter.subscribe_to_lock_miss(self.handle_limiter_miss)

        return limiter

    def update_otto_limiter(self):
        domains = self.cache.get_domain_limiters()

        if hasattr(self.otto, 'limiter') and self.otto.limiter is not None:
            self.otto.limiter.update_domain_definitions(*domains)

    def start_otto(self):
        self.info('Starting Octopus with %d concurrent threads.' % self.options.concurrency)
        self.otto = TornadoOctopus(
            concurrency=self.options.concurrency, cache=self.options.cache,
            connect_timeout_in_seconds=self.config.CONNECT_TIMEOUT_IN_SECONDS,
            request_timeout_in_seconds=self.config.REQUEST_TIMEOUT_IN_SECONDS,
            limiter=self.get_otto_limiter()
        )
        self.otto.start()

    def handle_error(self, exc_type, exc_value, tb):
        try:
            if not self.db.connection_invalidated:
                self.db.rollback()
        except Exception:
            err = sys.exc_info()[1]
            logging.error("Cannot rollback: %s" % str(err))

        self.otto.url_queue = []
        self.db.close_all()
        self.db.remove()
        self.db = scoped_session(self.sqlalchemy_db_maker)

        for handler in self.error_handlers:
            handler.handle_exception(
                exc_type, exc_value, tb, extra={
                    'worker-uuid': self.uuid,
                    'holmes-version': __version__
                }
            )

    def async_get(self, url, handler, method='GET', **kw):
        url, response = self.cache.get_request(url)

        if not response:
            kw['proxy_host'] = self.config.HTTP_PROXY_HOST
            kw['proxy_port'] = self.config.HTTP_PROXY_PORT

            self.debug('Enqueueing %s for %s...' % (method, url))
            self.otto.enqueue(url, self.handle_response(url, handler), method, **kw)
        else:
            handler(url, response)

    def handle_response(self, url, handler):
        def handle(url, response):
            self.cache.set_request(
                url, response.status_code, response.headers, response.cookies,
                response.text, response.effective_url, response.error, response.request_time,
                self.config.REQUEST_CACHE_EXPIRATION_IN_SECONDS
            )
            handler(url, response)
        return handle

    def handle_limiter_miss(self, url):
        pass

    def publish(self, data):
        self.redis_pub_sub.publish('events', data)


class HolmesWorker(BaseWorker):
    def initialize(self):
        self.uuid = uuid4().hex
        self.working_url = None
        self.domain_name = None
        self.last_ping = None

        authnz_wrapper_class = self.load_authnz_wrapper()
        if authnz_wrapper_class:
            self.authnz_wrapper = authnz_wrapper_class(self.config)
        else:
            self.authnz_wrapper = None

        self.facters = self._load_facters()
        self.validators = self._load_validators()
        self.error_handlers = [handler(self.config) for handler in self.load_error_handlers()]

        self.connect_sqlalchemy()

        self.search_provider = self.load_search_provider()(
            config=self.config,
            db=self.db,
            authnz_wrapper=self.authnz_wrapper
        )

        self.connect_to_redis()
        self.start_otto()

        self.fact_definitions = {}
        self.violation_definitions = {}

        self.default_violations_values = {}

        for facter in self.facters:
            self.fact_definitions.update(facter.get_fact_definitions())

        Key.insert_keys(self.db, self.fact_definitions)

        for validator in self.validators:
            self.violation_definitions.update(validator.get_violation_definitions())

            self.default_violations_values.update(
                validator.get_default_violations_values(self.config)
            )

        Key.insert_keys(
            self.db, self.violation_definitions, self.default_violations_values
        )

        self.configure_material_girl()

        DomainsViolationsPrefs.insert_default_violations_values_for_all_domains(
            self.db,
            self.default_violations_values,
            self.violation_definitions,
            self.cache
        )

        self.load_all_domains_violations_prefs()

    def load_all_domains_violations_prefs(self):
        from holmes.models import Domain

        for domain in Domain.get_all_domains(self.db):
            self.cache.get_domain_violations_prefs(domain.name)

    def config_parser(self, parser):
        parser.add_argument(
            '--concurrency',
            '-t',
            type=int,
            default=10,
            help='Number of threads (or async http requests) to use for Octopus (doing GETs concurrently)'
        )

        parser.add_argument(
            '--cache', default=False, action='store_true',
            help='Whether http requests should be cached by Octopus.'
        )

    def get_description(self):
        uuid = str(getattr(self, 'uuid', ''))

        return "%s%sholmes-worker-%s%s" % (
            Fore.BLUE,
            Style.BRIGHT,
            uuid,
            Style.RESET_ALL,
        )

    def do_work(self):
        self.debug('Started doing work...')

        self.update_otto_limiter()
        job = self._load_next_job()

        if job is None:
            self.info('No jobs could be found! Returning...')
            self._ping_api()
            return

        if not self._start_job(job):
            self.info('Could not start job for url "%s". Maybe other worker doing it?' % job['url'])
            lock = job.get('lock', None)
            self._release_lock(lock)
            return

        self.info('Starting new job for %s...' % job['url'])
        self._start_reviewer(job=job)

        lock = job.get('lock', None)
        self._complete_job(lock)
        self.db.commit()

    def _start_reviewer(self, job):
        if job:

            if count_url_levels(job['url']) > self.config.MAX_URL_LEVELS:
                self.info('Max URL levels! Details: %s' % job['url'])
                return

            self.debug('Starting Review for [%s]' % job['url'])
            reviewer = Reviewer(
                api_url=self.config.HOLMES_API_URL,
                page_uuid=job['page'],
                page_url=job['url'],
                page_score=0,
                config=self.config,
                validators=self.validators,
                facters=self.facters,
                search_provider=self.search_provider,
                async_get=self.async_get,
                wait=self.otto.wait,
                wait_timeout=0,  # max time to wait for all requests to finish
                db=self.db,
                cache=self.cache,
                publish=self.publish,
                girl=self.girl,
                fact_definitions=self.fact_definitions,
                violation_definitions=self.violation_definitions
            )

            reviewer.review()

    def _ping_api(self):
        self.debug('Pinging that this worker is still alive...')

        self.last_ping = datetime.utcnow()

        self.publish(dumps({
            'type': 'worker-status',
            'workerId': str(self.uuid),
            'dt': self.last_ping,
            'url': self.working_url,
            'domainName': self.domain_name,
        }))

    def handle_limiter_miss(self, url):
        self.working_url = url

        if self.last_ping < datetime.utcnow() - timedelta(seconds=1):
            self._ping_api()

    def _load_next_job(self):
        return self.cache.get_next_job(self.config.REVIEW_EXPIRATION_IN_SECONDS, self.config.WORKERS_LOOK_AHEAD_PAGES)

    def _start_job(self, job):
        try:
            lock = Lock(job['url'], redis=self.redis, timeout=1)
            lock.acquire()

            self.working_url = job['url']

            if self.working_url:
                self.domain_name, domain_url = get_domain_from_url(self.working_url)

            self._ping_api()
            job['lock'] = lock

            return True
        except LockTimeout:
            job['lock'] = None
            return False

    def _complete_job(self, lock):
        self.working_url = None
        self.domain_name = None
        self._ping_api()
        self._release_lock(lock)
        Request.delete_old_requests(self.db, self.config)

    def _release_lock(self, lock):
        if lock is not None:
            lock.release()


def main():
    worker = HolmesWorker(sys.argv[1:])
    worker.run()

if __name__ == '__main__':
    main()
