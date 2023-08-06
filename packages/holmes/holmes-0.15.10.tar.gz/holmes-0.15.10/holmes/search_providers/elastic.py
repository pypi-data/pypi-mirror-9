#!/usr/bin/env python
# -*- coding: utf-8 -*-

from holmes.search_providers import SearchProvider

from holmes.models.keys import Key
from holmes.models.page import Page
from holmes.models.violation import Violation

from pyelasticsearch import ElasticSearch
from pyelasticsearch.exceptions import (
    Timeout, ConnectionError, ElasticHttpError, InvalidJsonResponseError
)
from tornado.concurrent import return_future
from tornadoes import ESConnection
from ujson import loads, dumps
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import joinedload

import logging
import time


class ElasticSearchProvider(SearchProvider):
    def __init__(self, config, db=None, authnz_wrapper=None, io_loop=None):
        self.debug = False
        self.config = config
        if db is not None:
            self.db = db
        self.syncES = ElasticSearch(
            '%(ELASTIC_SEARCH_PROTOCOL)s://%(ELASTIC_SEARCH_HOST)s:%(ELASTIC_SEARCH_PORT)s' % config
        )
        self.asyncES = ESConnection(
            host=config.get('ELASTIC_SEARCH_HOST'),
            port=config.get('ELASTIC_SEARCH_PORT'),
            io_loop=io_loop,
            protocol=config.get('ELASTIC_SEARCH_PROTOCOL'),
        )
        self.index = config.get('ELASTIC_SEARCH_INDEX')
        self.max_retries = config.get('ELASTIC_SEARCH_MAX_RETRIES')

    def activate_debug(self):
        self.debug = True

    def connect_to_db(self):
        from sqlalchemy import create_engine
        from sqlalchemy.orm import scoped_session, sessionmaker
        conn_string = self.config.get('SQLALCHEMY_CONNECTION_STRING')
        engine = create_engine(
            conn_string,
            convert_unicode=True,
            pool_size=1,
            max_overflow=0,
            echo=self.debug
        )
        maker = sessionmaker(bind=engine, autoflush=True)
        self.db = scoped_session(maker)

    def _assemble_inner_query(self, domain=None, page_filter=None):
        if page_filter and domain:
            page_prefix = '%s/%s' % (domain.url, page_filter)
        else:
            page_prefix = None

        if page_prefix:
            return {
                'prefix': {
                    'page_url': page_prefix
                }
            }
        else:
            return {
                'match_all': {}
            }

    def _assemble_outer_query(self, inner_query, filter_terms):
        return {
            'filtered': {
                'query': inner_query,
                'filter': {
                    'and': [{
                        'term': filter_term
                    } for filter_term in filter_terms]
                }
            }
        }

    def _assemble_filter_terms(self, key_id=None, domain=None):
        filter_terms = []

        if key_id:
            filter_terms.append({'keys.id': key_id})

        if domain:
            filter_terms.append({'domain_id': domain.id})

        return filter_terms

    def gen_doc(self, review):
        return {
            'keys': [{'id': violation.key_id} for violation in review.violations],
            'uuid': str(review.uuid),
            'completed_date': review.completed_date,
            'violation_count': review.violation_count,
            'page_id': review.page_id,
            'page_uuid': str(review.page.uuid),
            'page_url': review.page.url,
            'page_last_review_date': review.page.last_review_date,
            'domain_id': review.domain_id,
            'domain_name': review.domain.name,
        }

    def index_review(self, review):
        for attempt in range(self.max_retries):
            try:
                self.syncES.send_request(
                    method='POST',
                    path_components=[self.index, 'review', review.page_id],
                    body=dumps(self.gen_doc(review)),
                    encode_body=False
                )
                break
            except (Timeout, ConnectionError, ElasticHttpError, InvalidJsonResponseError) as e:
                values = review.id, review.page_id, str(e)
                logging.error('Could not index review (review_id:{0}, page_id:{1}): {2}'.format(*values))
                time.sleep(1)
                if attempt >= self.max_retries - 1:
                    raise
            else:
                raise

    def index_reviews(self, reviewed_pages, reviews_count, batch_size):
        action = {'index': {'_type': 'review'}}

        for i in range(0, reviews_count, batch_size):
            body_bits = []

            for page in reviewed_pages[i:i + batch_size]:
                doc = self.gen_doc(page.last_review)

                action['index']['_id'] = doc['page_id']

                body_bits.append(dumps(action))
                body_bits.append(dumps(doc))

            # Yes, that trailing newline IS necessary
            body = '\n'.join(body_bits) + '\n'

            self.syncES.send_request(
                method='POST',
                path_components=[self.index, '_bulk'],
                body=body,
                encode_body=False
            )

        logging.info('Done!')

    @return_future
    def get_by_violation_key_name(self, key_id, current_page=1, page_size=10, domain=None, page_filter=None, callback=None):
        def treat_response(response):
            if response.error is None:
                try:
                    hits = loads(response.body).get('hits', {'hits': []})

                    reviews_data = []
                    for hit in hits['hits']:
                        completedAt = datetime.utcfromtimestamp(hit['_source']['completed_date'])
                        reviews_data.append({
                            'uuid': hit['_source']['uuid'],
                            'page': {
                                'uuid': hit['_source']['page_uuid'],
                                'url': hit['_source']['page_url'],
                                'completedAt': completedAt
                            },
                            'domain': hit['_source']['domain_name']
                        })

                    reviews_count = hits.get('total', 0)

                    callback({
                        'reviews': reviews_data,
                        'reviewsCount': reviews_count
                    })
                except Exception as e:
                    reason = 'ElasticSearchProvider: invalid response (%s [%s])' % (type(e), e.message)
                    logging.error(reason)
                    callback({'error': {'status_code': 500, 'reason': reason}})
            else:
                reason = 'ElasticSearchProvider: erroneous response (%s [%s])' % (response.error.message, response.body)
                logging.error(reason)
                callback({'error': {'status_code': 500, 'reason': reason}})

        inner_query = self._assemble_inner_query(domain, page_filter)
        filter_terms = self._assemble_filter_terms(key_id, domain)

        query = self._assemble_outer_query(inner_query, filter_terms)

        sort_ = [{
            'completed_date': {
                'order': 'desc'
            }
        }, {
            'violation_count': {
                'order': 'desc'
            }
        }]

        source = {'query': query, 'sort': sort_}

        self.asyncES.search(
            callback=treat_response,
            index=self.index,
            type='review',
            source=source,
            page=current_page,
            size=page_size,
        )

    @return_future
    def get_domain_active_reviews(self, domain, current_page=1, page_size=10, page_filter=None, callback=None):
        def treat_response(response):
            if response.error is None:
                try:
                    hits = loads(response.body).get('hits', {'hits': []})

                    pages = []
                    for hit in hits['hits']:
                        completedAt = datetime.utcfromtimestamp(hit['_source']['completed_date'])
                        pages.append({
                            'url': hit['_source']['page_url'],
                            'uuid': hit['_source']['page_uuid'],
                            'violationCount': len(hit['_source']['keys']),
                            'completedAt': completedAt,
                            'reviewId': hit['_source']['uuid']
                        })

                    reviews_count = hits.get('total', 0)

                    callback({
                        'reviewsCount': reviews_count,
                        'pages': pages
                    })
                except Exception as e:
                    reason = 'ElasticSearchProvider: invalid response (%s [%s])' % (type(e), e.message)
                    logging.error(reason)
                    callback({'error': {'status_code': 500, 'reason': reason}})
            else:
                reason = 'ElasticSearchProvider: erroneous response (%s [%s])' % (response.error.message, response.body)
                logging.error(reason)
                callback({'error': {'status_code': 500, 'reason': reason}})

        inner_query = self._assemble_inner_query(domain=domain, page_filter=page_filter)
        filter_terms = self._assemble_filter_terms(domain=domain)

        query = self._assemble_outer_query(inner_query, filter_terms)

        sort_ = [{
            'violation_count': {
                'order': 'desc'
            }
        }, {
            'completed_date': {
                'order': 'desc'
            }
        }]

        source = {'query': query, 'sort': sort_}

        self.asyncES.search(
            callback=treat_response,
            index=self.index,
            type='review',
            source=source,
            page=current_page,
            size=page_size,
        )

    def refresh(self):
        try:
            self.syncES.refresh(index=self.index)
        except Exception as e:
            logging.error('Could not refresh index (%s)' % e)

    def get_index_settings(cls):
        return {
            'index': {
                'number_of_shards': 4
            }
        }

    def get_index_mapping(cls):
        return {
            'review': {
                'properties': {
                    'keys': {
                        'properties': {
                            'id': {
                                'type': 'integer'
                            }
                        }
                    },
                    'uuid': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    },
                    'completed_date': {
                        'type': 'integer'
                    },
                    'violation_count': {
                        'type': 'float'
                    },
                    'page_id': {
                        'type': 'integer'
                    },
                    'page_uuid': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    },
                    'page_url': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    },
                    'page_last_review_date': {
                        'type': 'integer'
                    },
                    'domain_id': {
                        'type': 'integer'
                    },
                    'domain_name': {
                        'type': 'string',
                        'index': 'not_analyzed'
                    }
                }
            }
        }

    def setup_index(self):
        try:
            settings = self.get_index_settings()
            self.syncES.create_index(index=self.index, settings=settings)
            mapping = self.get_index_mapping()
            self.syncES.put_mapping(index=self.index, doc_type='review', mapping=mapping)
            logging.info('Index %s created.' % self.index)
        except Exception as e:
            raise e

    def delete_index(self):
        try:
            self.syncES.delete_index(index=self.index)
            logging.info('Index %s deleted.' % self.index)
        except Exception as e:
            raise e

    def _get_max_page_id_from_index(self, must_have_domain_name=False):
        if must_have_domain_name:
            inner_query = {
                'constant_score': {
                    'filter': {
                        'not': {
                            'missing': {
                                'field': 'domain_name'
                            }
                        }
                    }
                }
            }
        else:
            inner_query = {
                'match_all': {}
            }

        query = {
            'query': inner_query,
            'sort': [{
                'page_id': {
                    'order': 'desc'
                }
            }]
        }

        results = self.syncES.search(query, index=self.index, doc_type='review')
        if results['hits']['total'] > 0:
            return results['hits']['hits'][0]['_id'] or 0
        return 0

    def index_all_reviews(self, keys=None, batch_size=200, replace=False):
        logging.info('Querying database...')
        self.connect_to_db()

        if keys is not None:
            keys = [k.id for k in self.db.query(Key.id).filter(Key.name.in_(keys)).all()]

        try:
            max_page_id = self._get_max_page_id_from_index(must_have_domain_name=True)
        except Exception:
            logging.error('Could not retrieve max page_id! Use with --replace (with caution)')
            return

        def apply_filters(query):
            if keys is not None:
                query = query \
                    .filter(Violation.review_id == Page.last_review_id) \
                    .filter(Violation.key_id.in_(keys))

            if not replace:
                query = query.filter(Page.id > max_page_id)

            return query.filter(Page.last_review_id != None)

        reviews_count = apply_filters(self.db.query(func.count(Page))).scalar()

        query = self.db.query(Page).options(joinedload('last_review'))
        reviewed_pages = apply_filters(query).order_by(Page.id.asc())

        logging.info('Indexing %d reviews...' % reviews_count)

        self.index_reviews(reviewed_pages, reviews_count, batch_size)

    @classmethod
    def new_instance(cls, config):
        return ElasticSearchProvider(config)

    @classmethod
    def main(cls):
        import sys

        parser = cls.argparser()
        args = parser.parse_args()

        config = {}
        host = None
        port = None
        index = None
        es = None

        levels = ['ERROR', 'WARNING', 'INFO', 'DEBUG']
        log_level = levels[args.verbose]
        logging.basicConfig(level=getattr(logging, log_level), format='%(levelname)s - %(message)s')

        if not (args.create or args.recreate or args.delete or args.keys or args.all_keys):
            parser.print_help()
            sys.exit(1)

        if args.conf:
            from derpconf.config import ConfigurationError
            from holmes.config import Config
            try:
                config = Config().load(args.conf[0])
                host = config['ELASTIC_SEARCH_HOST']
                port = config['ELASTIC_SEARCH_PORT']
                index = config['ELASTIC_SEARCH_INDEX']
            except ConfigurationError:
                logging.error('Could not load config! Use --conf conf_file')
                sys.exit(1)
            except KeyError:
                logging.error('Could not parse config! Check it\'s contents')
                sys.exit(1)

        if args.server:
            try:
                host, port = args.server[0].split(':')
                config['ELASTIC_SEARCH_HOST'] = host
                config['ELASTIC_SEARCH_PORT'] = port
            except Exception:
                logging.error('Could not parse server host and port! Use --server host:port')
                sys.exit(1)

        if args.index:
                index = args.index[0]
                config['ELASTIC_SEARCH_INDEX'] = index

        from pyelasticsearch.exceptions import IndexAlreadyExistsError, ElasticHttpNotFoundError, InvalidJsonResponseError
        from requests.exceptions import ConnectionError
        try:

            if args.create or args.recreate or args.delete:
                if host is None or port is None:
                    logging.error('Need either a host and port or a config file to perform such operation!')
                    sys.exit(1)
                if index is None:
                    logging.error('Need either an index name or a config file to perform such operation!')
                    sys.exit(1)
                else:
                    es = cls.new_instance(config)
                    if args.recreate or args.delete:
                        try:
                            es.delete_index()
                        except ElasticHttpNotFoundError:
                            pass
                        except InvalidJsonResponseError as e:
                            logging.error('Invalid response! Reason: %s' % e)
                            sys.exit(1)
                    if args.create or args.recreate:
                        es.setup_index()

            if args.keys or args.all_keys:
                if config is None:
                    logging.error('Need a config file to perform such operation! Use --conf conf_file')
                else:
                    batch_size = args.batch_size[0] if args.batch_size else 200
                    es = cls.new_instance(config) if not es else es
                    try:
                        if args.verbose > 2:
                            es.activate_debug()
                        if args.keys:
                            es.index_all_reviews(args.keys, replace=args.replace, batch_size=batch_size)
                        elif args.all_keys:
                            es.index_all_reviews(replace=args.replace, batch_size=batch_size)
                    except InvalidJsonResponseError as e:
                        logging.error('Invalid response! Reason: %s' % e)
                        sys.exit(1)

        except IndexAlreadyExistsError:
            logging.error('Index %s already exists! Use --recreate (with caution) to recreate' % index)
        except ConnectionError:
            logging.error('Could not connect to server at %s:%s' % (host, port))
        except KeyError:
            logging.error('Could not get host nor port! Use either -conf or --server')
            sys.exit(1)

if __name__ == '__main__':
    ElasticSearchProvider.main()
