#!/usr/bin/python
# -*- coding: utf-8 -*-

from holmes.validators.base import Validator
from holmes.utils import _


class BodyValidator(Validator):
    @classmethod
    def get_violation_definitions(cls):
        return {
            'page.body.not_found': {
                'title': _('Page body not found'),
                'description': _('Body was not found on %s.'),
                'category': _('Semantics'),
                'generic_description': _(
                    'The <body> tag defines the documents body\'s, it\'s contains '
                    'all the content of an HTML document. The ausence of a this tag '
                    'represents a no content and sematically invalid webpage.'
                ),
            }
        }

    def validate(self):
        body = self.get_body()

        if not body:

            page_url = self.reviewer.page_url

            self.add_violation(
                key='page.body.not_found',
                value=page_url,
                points=50
            )

    def get_body(self):
        return self.review.data.get('page.body', None)
