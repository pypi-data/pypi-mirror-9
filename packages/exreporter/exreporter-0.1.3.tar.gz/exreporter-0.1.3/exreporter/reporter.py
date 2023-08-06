# -*- coding: utf-8 -*-

import os

from .formats import Formats
from .stack_trace import StackTrace


class Reporter(object):

    def __init__(self, store, max_comments=50,
                 time_delta=10, include_locals=True, labels=['Bugs']):
        '''Initialize reporter object with issue attributes and other settings.

        :params store: object of store eg: 'stores.github.GithubStore'
        :params title_format: (optional) string to specify the format of issue title
        :params body_format: (optional) string to specify the format of issue body
        :params extra_content: (optional) extra content that is to be added to issue body
        :params max_comments: (optional) maximum number of comments after which new issue is to be created, default value is ``50``
        :params time_delta: (optional) specifies minimum time interval after which issue should be reported if the exceptions occurs multiple times
        :params include_locals: (optional) boolean specifying whether dump of ``locals`` should be included in issue body
        :params labels: (optional) list of labels that are to be applied to the issue, default: ``['Bug']``
        '''
        self.max_comments = max_comments
        self.time_delta = time_delta
        self.include_locals = include_locals
        self.labels = labels
        self.store = store

    def report(self, **kwargs):
        trace_info = StackTrace()
        title_format = kwargs.pop('title_format', Formats.title)
        body_format = kwargs.pop('body_format', Formats.body)

        max_comments = kwargs.get('max_comments', self.max_comments)
        time_delta = kwargs.get('time_delta', self.time_delta)
        include_locals = kwargs.get('include_locals', self.include_locals)
        labels = kwargs.get('labels', self.labels)

        culprit = Formats.culprit.format(
            filepath=trace_info.filepath, lineno=trace_info.lineno,
            exception=trace_info.exception.__name__)

        title = title_format.format(
            exception=trace_info.exception.__name__,
            filename=os.path.basename(trace_info.filepath),
            method_name=trace_info.method_name)

        body = "{}".format(
            body_format.format(stack_trace=trace_info.stack_trace_text))

        if include_locals:
            body = "{} {}".format(
                body, Formats.locals_format.format(
                    locals_data=trace_info.locals_data)
            )

        extra_content = kwargs.pop('extra_content', '')

        if extra_content:
            body = "{}\n\nExtra Content:\n{}".format(
                body, extra_content
            )

        if kwargs.get('request'):
            body = "{} {}".format(
                body, Formats.request_data.format(
                    request_data=str(kwargs.get('request'))
                )
            )

        body = """{}

{}
""".format(body, culprit)
        return self.store.create_or_update_issue(
            title=title, body=body, culprit=culprit, max_comments=max_comments,
            time_delta=time_delta, labels=labels)
