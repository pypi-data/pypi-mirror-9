#!/usr/bin/python
# -*- coding: utf-8 -*-

from os.path import join

# Deferred imports
try:
    from urllib.parse import urlparse  # Py3
except ImportError:
    from urlparse import urlparse

import inspect
import email.utils as eut
from datetime import datetime

import codecs
from box.util.rotunicode import RotUnicode
codecs.register(RotUnicode.search_function)

import lxml.html
import logging

from holmes.config import Config
from holmes.facters import Facter
from holmes.validators.base import Validator
from holmes.models import Page
from holmes.utils import get_domain_from_url


class InvalidReviewError(RuntimeError):
    pass


class ReviewDAO(object):
    def __init__(self, page_uuid, page_url, last_modified=None, expires=None):
        self.page_uuid = page_uuid
        self.page_url = page_url
        self.last_modified = last_modified
        self.expires = expires
        self.facts = {}
        self.violations = []
        self.data = {}
        self._current = None
        self.requests = []

    def add_fact(self, key, value):
        self.facts[key] = {
            'key': key,
            'value': value
        }

    def add_violation(self, key, value, points):
        self.violations.append({
            'key': key,
            'value': value,
            'points': points
        })

    def to_dict(self):
        return {
            'page_uuid': self.page_uuid,
            'page_url': self.page_url,
            'facts': self.facts.values(),
            'violations': self.violations,
            'lastModified': self.last_modified,
            'expires': self.expires,
            'requests': self.requests
        }


class Reviewer(object):
    def __init__(
            self, api_url, page_uuid, page_url, page_score,
            config=None, validators=[], facters=[], search_provider=None, async_get=None,
            wait=None, wait_timeout=None, db=None, cache=None, publish=None,
            fact_definitions=None, violation_definitions=None, girl=None):

        self.db = db
        self.cache = cache
        self.girl = girl
        self.publish = publish

        self.api_url = api_url

        self.page_uuid = page_uuid
        self.page_url = page_url
        self.page_score = page_score

        self.domain_name, self.domain_url = get_domain_from_url(self.page_url)

        self.ping_method = None

        self.review_dao = ReviewDAO(self.page_uuid, self.page_url)

        assert isinstance(config, Config), 'config argument must be an instance of holmes.config.Config'
        self.config = config

        for facter in facters:
            message = 'All facters must subclass holmes.facters.Facter (Error: %s)' % facter.__class__.__name__
            assert inspect.isclass(facter), message
            assert issubclass(facter, Facter), message

        for validator in validators:
            message = 'All validators must subclass holmes.validators.base.Validator (Error: %s)' % validator.__class__.__name__
            assert inspect.isclass(validator), message
            assert issubclass(validator, Validator), message

        self.validators = validators
        self.facters = facters

        self.search_provider = search_provider

        self.responses = {}
        self.raw_responses = {}
        self.status_codes = {}

        self.async_get_func = async_get
        self._wait_for_async_requests = wait
        self._wait_timeout = wait_timeout

        self.fact_definitions = fact_definitions
        self.violation_definitions = violation_definitions

    def get_domains_violations_prefs_by_key(self, key_name):
        if key_name is None:
            return None

        if self.violation_definitions is None:
            return None

        default_value = None

        key = self.violation_definitions.get(key_name, None)
        if key is not None:
            default_value = key.get('default_value')

        domains_prefs = self.cache.get_domain_violations_prefs(self.domain_name)

        if domains_prefs:
            item = next((item for item in domains_prefs if item['key'] == key_name), None)
            if item:
                return item['value']

        return default_value

    def ping(self):
        if self.ping_method is not None:
            self.ping_method()

    def _async_get(self, url, handler, method='GET', **kw):
        if self.async_get_func:
            self.async_get_func(url, self.handle_async_get(handler), method, **kw)

    def handle_async_get(self, handler):
        def handle(url, response):
            if not hasattr(response, 'from_cache') or not response.from_cache:
                response.from_cache = False
                self.review_dao.requests.append((url, response))

            handler(url, response)

        return handle

    def review(self):
        self.load_content(self.content_loaded)
        self.wait_for_async_requests()

    def load_content(self, callback):
        self._async_get(self.page_url, callback)

    def content_loaded(self, url, response):
        if response.status_code > 399 or response.text is None:
            if response.text:
                headers = None
                if response.status_code == 404:
                    text = None
                else:
                    text = response.text.decode('rotunicode')
            else:
                text = 'Empty response.text'
                headers = response.headers

            msg = "Could not load '%s' (%s) - %s!" % (url,
                                                      response.status_code,
                                                      text)
            logging.error(msg)
            if headers is not None:
                logging.warning('Response is from cache: %s' % response.from_cache)
                logging.warning('Headers for "%s": %s' % (url, headers))
            return

        logging.debug('Content for url %s loaded.' % url)

        last_modified = None

        modified = response.headers.get('Last-Modified', None)
        if modified is not None:
            date = eut.parsedate(modified)
            if date is not None:
                last_modified = datetime(*date[:6])

        self.review_dao.last_modified = last_modified

        expires = None

        expires_key = response.headers.get('Expires', None)
        if expires_key:
            date = eut.parsedate(expires_key)
            if date is not None:
                expires = datetime(*date[:6])

        self.review_dao.expires = expires

        self._current = response

        try:
            self._current.html = lxml.html.fromstring(response.text)
        except (lxml.etree.XMLSyntaxError, lxml.etree.ParserError):
            self._current.html = None

        self.run_facters()
        self.wait_for_async_requests()

        self.run_validators()
        self.wait_for_async_requests()

        self.save_review()

    @property
    def current(self):
        return self._current

    @property
    def current_html(self):
        if not hasattr(self.current, 'html') or self.current.html is None:
            return lxml.html.HtmlElement()
        else:
            return self.current.html

    def run_facters(self):
        for facter in self.facters:
            self.ping()
            logging.debug('---------- Started running facter %s ---------' % facter.__name__)
            facter_instance = facter(self)
            facter_instance.get_facts()

    def run_validators(self):
        for validator in self.validators:
            self.ping()
            logging.debug('---------- Started running validator %s ---------' % validator.__name__)
            validator_instance = validator(self)
            validator_instance.validate()

    def get_url(self, url):
        return join(self.api_url.rstrip('/'), url.lstrip('/'))

    def enqueue(self, urls):
        if not urls:
            return

        for url, score in urls:
            Page.add_page(
                self.db,
                self.cache,
                url,
                score,
                self.async_get_func,
                self.publish,
                self.config,
                self.girl,
                self.violation_definitions,
                self.handle_page_added
            )

        self.wait_for_async_requests()

    def handle_page_added(self, (url, result, page)):
        if not result:
            error_message = "Could not enqueue page '" + url + "'! Error: %s"
            logging.error(error_message % page)

        self.ping()

    def add_fact(self, key, value):
        self.review_dao.add_fact(key, value)

    def add_violation(self, key, value, points):
        self.review_dao.add_violation(key, value, points)

    def save_review(self):
        from holmes.models import Review

        data = self.review_dao.to_dict()

        Review.save_review(
            self.page_uuid, data, self.db, self.search_provider,
            self.fact_definitions, self.violation_definitions,
            self.cache, self.publish, self.config
        )

    def wait_for_async_requests(self):
        self._wait_for_async_requests(self._wait_timeout)

    def is_root(self):
        result = urlparse(self.page_url)
        return '{0}://{1}'.format(result.scheme, result.netloc) == self.page_url.rstrip('/')
