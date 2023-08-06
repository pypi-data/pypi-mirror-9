# -*- coding: utf-8 -*-

"""
test_reporter
----------------------------------

Tests for `exreporter.reporter` module.
"""

import unittest
from mock import patch, MagicMock

from exreporter.reporter import Reporter


class TestReporter(unittest.TestCase):

    @patch('exreporter.reporter.Formats')
    @patch('exreporter.reporter.StackTrace')
    def test_reporter_report_with_defaults(self, StackTrace, Formats):
        store = MagicMock()
        stack_trace = StackTrace()
        stack_trace.exception = ValueError

        reporter = Reporter(store=store)

        reporter.report()

        store.create_or_update_issue.assert_called_once_with(
            title=Formats.title.format(),
            culprit=Formats.culprit.format(),
            body='''{} {}

{}
'''.format(Formats.body.format(),
           Formats.locals_format.format(),
           Formats.culprit.format()),
            labels=reporter.labels, time_delta=reporter.time_delta,
            max_comments=reporter.max_comments)
