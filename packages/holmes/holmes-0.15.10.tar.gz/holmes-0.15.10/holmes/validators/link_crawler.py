#!/usr/bin/python
# -*- coding: utf-8 -*-

import re

from holmes.validators.base import Validator
from holmes.utils import get_domain_from_url, _

REMOVE_HASH = re.compile('([#].*)$')


class LinkCrawlerValidator(Validator):
    def __init__(self, *args, **kw):
        super(LinkCrawlerValidator, self).__init__(*args, **kw)
        self.broken_links = set()
        self.moved_links = set()

    @classmethod
    def get_links_parsed_value(cls, value):
        return {'links': ', '.join([
            '<a href="%s" target="_blank">Link #%s</a>' % (url, index)
            for index, url in enumerate(value)
        ])}

    @classmethod
    def get_violation_definitions(cls):
        return {
            'link.broken': {
                'title': _('Broken link(s) found'),
                'description': _(
                    'This page contains broken links to %(links)s '
                    '(the urls failed to load or timed-out after 10 seconds). '
                    'This can lead your site to lose rating with '
                    'search engines and is misleading to users.'),
                'value_parser': cls.get_links_parsed_value,
                'category': _('HTTP'),
                'generic_description': _(
                    'Validates hyperlinks with a invalid resource. '
                    'The pointed resource can be a Client or a '
                    'Server Error, they can be timeout load or, '
                    'in most cases, means a not founded page.'
                )
            },
            'link.moved.temporarily': {
                'title': _('Moved Temporarily'),
                'description': _(
                    'A link from your page to "%(links)s" is using a 302 or '
                    '307 redirect. It passes 0%% of link juice (ranking '
                    'power) and, in most cases, should not be used. Use '
                    '301 instead.'),
                'value_parser': cls.get_links_parsed_value,
                'category': _('HTTP'),
                'generic_description': _(
                    'Validates links that uses a 302 or 307 redirect. '
                    'In this cases, it passes 0% of link juice (ranking '
                    'power) and, in most cases, should not be used. Use of '
                    '301 is recommended.'
                )
            }
        }

    def validate(self):
        links = self.get_links()

        total_score = float(self.reviewer.page_score)
        tax = total_score * float(self.reviewer.config.PAGE_SCORE_TAX_RATE)
        available_score = total_score - tax

        number_of_links = float(len(links)) or 1.0
        link_score = available_score / number_of_links

        for url, response in links:
            domain, domain_url = get_domain_from_url(url)
            if domain in self.page_url:
                self.send_url(response.effective_url, link_score, response)
            else:
                if response.status_code in [302, 307]:
                    self.moved_link_violation(url, response)
                elif response.status_code > 399:
                    self.broken_link_violation(url, response)

        if self.broken_links:
            self.add_violation(
                key='link.broken',
                value=self.broken_links,
                points=100 * len(self.broken_links)
            )

        if self.moved_links:
            self.add_violation(
                key='link.moved.temporarily',
                value=self.moved_links,
                points=100
            )

        self.flush()

    def flush(self, *args, **kw):
        super(LinkCrawlerValidator, self).flush(*args, **kw)
        self.broken_links = set()
        self.moved_links = set()

    def get_links(self):
        return self.review.data['page.links']

    def broken_link_violation(self, url, response):
        self.broken_links.add(url)

    def moved_link_violation(self, url, response):
        self.moved_links.add(url)
