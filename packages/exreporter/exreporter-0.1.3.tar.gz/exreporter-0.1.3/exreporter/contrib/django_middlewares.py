# -*- coding: utf-8 -*-

"""
exporter.contrib.django_middlewares
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This module implements Django middlewares for different stores.
Requires following Django settings to be present:
- EXREPORTER_GITHUB_USER
- EXREPORTER_GITHUB_REPO
- EXREPORTER_GITHUB_AUTH_TOKEN
- EXREPORTER_GITHUB_LABELS

:copyright: (c) 2014 by Vedarth Kulkarni.
:license: MIT, see LICENSE for more details.

"""

from django.conf import settings
from exreporter.credentials import GithubCredentials
from exreporter.stores import GithubStore
from exreporter import ExReporter


class ExreporterGithubMiddleware(object):
    """Exreporter middleware for Django framework.
    """

    def process_exception(self, request, exception):
        """Report exceptions from requests via Exreporter.
        """
        gc = GithubCredentials(
            user=settings.EXREPORTER_GITHUB_USER,
            repo=settings.EXREPORTER_GITHUB_REPO,
            auth_token=settings.EXREPORTER_GITHUB_AUTH_TOKEN)
        gs = GithubStore(credentials=gc)
        reporter = ExReporter(
            store=gs, labels=settings.EXREPORTER_GITHUB_LABELS)

        reporter.report()
