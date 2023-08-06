#!/usr/bin/python
# -*- coding: utf-8 -*-


from holmes.validators.base import Validator
from holmes.utils import _


class RobotsValidator(Validator):

    SITEMAP_NOT_FOUND = _('You must specify the location of the Sitemap '
                          'using a robots.txt file')

    DISALLOW_NOT_FOUND = _('Disallow directive indicates that robots should '
                           'not access the specific directory, subdirectory '
                           'or file. ')

    DISALLOW_ROOT_PATH = _('Crawlers may not index anything, because '
                           'the root path (/) is disallowed.')

    @classmethod
    def get_violation_definitions(cls):
        return {
            'robots.not_found': {
                'title': _('Robots file not found'),
                'description': _("The robots file at '%s' was not found."),
                'category': _('SEO'),
                'generic_description': _(
                    'Validates the presence of robots file. A robots.txt file tells a search '
                    'engine what content they will index or not.'
                )
            },
            'robots.empty': {
                'title': _('Robots file was empty'),
                'description': _("The robots file at '%s' was empty."),
                'category': _('SEO'),
                'generic_description': _(
                    'Validates the content of a robots file. If empty, the search engines '
                    'will understand that has no robots file present.'
                )
            },
            'robots.sitemap.not_found': {
                'title': _('Sitemap in Robots not found'),
                'description': cls.SITEMAP_NOT_FOUND,
                'category': _('SEO'),
                'generic_description': _(
                    'Validates the presence of Sitemap in Robots.txt. '
                    'The Sitemap tells the robot how your website is '
                    'organized and witch way can be indexed.'
                )
            },
            'robots.disallow.not_found': {
                'title': _('Disallow in Robots not found'),
                'description': cls.DISALLOW_NOT_FOUND,
                'category': _('SEO'),
                'generic_description': _(
                    'Validates the presence of Disallow in Robots.txt. '
                    'Disallow lists the files and directories to be '
                    'excluded from indexing'
                )
            },
            'robots.disallow.root_path': {
                'title': _('Disallow: / in Robots'),
                'description': cls.DISALLOW_ROOT_PATH,
                'category': _('SEO'),
                'generic_description': _(
                    'Validates if the root path of your site is in '
                    'Disallow directive of Robots.txt. If true, the '
                    'root of your site will not be indexed on search '
                    'engines.'
                )
            },
        }

    def validate(self):
        if not self.reviewer.is_root():
            return

        response = self.review.data['robots.response']

        if response.status_code > 399:
            self.add_violation(
                key='robots.not_found',
                value=response.url,
                points=100
            )
            return

        if not response.text.strip():
            self.add_violation(
                key='robots.empty',
                value=response.url,
                points=100
            )
            return

        has_sitemap = False

        has_disallow = False
        disallow_root_path = False

        for rawline in response.text.splitlines():
            line = rawline.strip()
            comments = line.find('#')
            if comments >= 0:
                line = line[:comments]
            if line == '' or ':' not in line:
                continue
            key, val = [x.strip() for x in line.split(':', 1)]
            key = key.lower()
            if key == 'sitemap':
                has_sitemap = True
            elif key == 'disallow':
                has_disallow = True
                if val == '/':
                    disallow_root_path = True

        if not has_sitemap:
            self.add_violation(
                key='robots.sitemap.not_found',
                value=None,
                points=100
            )

        if not has_disallow:
            self.add_violation(
                key='robots.disallow.not_found',
                value=None,
                points=100
            )
        elif disallow_root_path:
            self.add_violation(
                key='robots.disallow.root_path',
                value=None,
                points=100
            )
