# -*- coding: utf-8 -*-

"""
exporter.stores.github
~~~~~~~~~~~~~~~~~

This module implements Github issue store for exporter.
:copyright: (c) 2014 by Vedarth Kulkarni.
:license: MIT, see LICENSE for more details.

"""

import json
import pytz
import datetime
import requests
from dateutil.tz import tzlocal


class GithubCredentials(object):
    """Github credentials.

    Necessary credentials to access/create/update issues on Github.

    Basic Usage:

      >>> from exporter.stores.github import GithubCredentials
      >>> gc = GithubCredentials(user="username", repo="repo name", auth_token="personla auth token")
    """

    def __init__(self, user, repo, auth_token):
        self.user, self.repo, self.auth_token = user, repo, auth_token


class GithubStore(object):
    """Github Issue Store.
    """

    def __init__(self, credentials):
        '''Initializes Github issue store.

        :params credentials: object of :class:`GithubCredentials` with proper credentials
        '''
        assert type(credentials) is GithubCredentials,\
            'Credentials object is not of type GithubCredentials'
        self.credentials = credentials
        self.github_request = GithubRequest(credentials=credentials)

    def create_or_update_issue(self, title, body, culprit, labels, **kwargs):
        '''Creates or comments on existing issue in the store.

        :params title: title for the issue
        :params body: body, the content of the issue
        :params culprit: string used to identify the cause of the issue,
            also used for aggregation
        :params labels: (optional) list of labels attached to the issue
        :returns: issue object
        :rtype: :class:`exreporter.stores.github.GithubIssue`
        '''
        issues = self.search(q=culprit, labels=labels)
        self.time_delta = kwargs.pop('time_delta')
        self.max_comments = kwargs.pop('max_comments')

        if issues:
            latest_issue = issues.pop(0)
            return self.handle_issue_comment(
                issue=latest_issue, title=title, body=body, **kwargs)
        else:
            return self.create_issue(
                title=title, body=body, **kwargs)

    def search(self, q, labels, state='open,closed', **kwargs):
        """Search for issues in Github.

        :param q: query string to search
        :param state: state of the issue
        :returns: list of issue objects
        :rtype: list

        """
        search_result = self.github_request.search(q=q, state=state, **kwargs)
        if search_result['total_count'] > 0:
            return list(
                map(lambda issue_dict: GithubIssue(
                    github_request=self.github_request, **issue_dict),
                    search_result['items'])
            )

    def handle_issue_comment(self, issue, title, body, **kwargs):
        """Decides whether to comment or create a new issue when trying to comment.

        :param issue: issue on which the comment is to be added
        :param title: title of the issue if new one is to be created
        :param body: body of the issue/comment to be created
        :returns: newly created issue or the one on which comment was created
        :rtype: :class:`exreporter.stores.github.GithubIssue`

        """
        if self._is_time_delta_valid(issue.updated_time_delta):
            if issue.comments_count < self.max_comments:
                issue.comment(body=body)
                return issue
            else:
                return self.create_issue(title=title, body=body, **kwargs)

    def _is_time_delta_valid(self, delta):
        return delta > self.time_delta

    def create_issue(self, title, body, labels=None):
        """Creates a new issue in Github.

        :params title: title of the issue to be created
        :params body: body of the issue to be created
        :params labels: (optional) list of labels for the issue
        :returns: newly created issue
        :rtype: :class:`exreporter.stores.github.GithubIssue`
        """
        kwargs = self.github_request.create(
            title=title, body=body, labels=labels)
        return GithubIssue(github_request=self.github_request, **kwargs)


class GithubIssue(object):
    """Python object representation of issue on Github.
    """

    def __init__(self, github_request, **kwargs):
        """Initializes Github issue object.
        For **kwargs please refer Github's documentation:
        https://developer.github.com/v3/issues/#get-a-single-issue

        :params github_request: object of :class:`GithubRequest` used to make HTTP requests to Github
        """
        self.github_request = github_request
        for attr, value in kwargs.items():
            setattr(self, attr, value)

    @property
    def comments_count(self):
        """Returns number of comments on the issue.
        """
        return int(self.comments)

    @property
    def updated_time_delta(self):
        """Returns the number of seconds ago the issue was updated from current time.
        """
        local_timezone = tzlocal()
        update_at = datetime.datetime.strptime(self.updated_at, '%Y-%m-%dT%XZ')
        update_at_utc = pytz.utc.localize(update_at)
        update_at_local = update_at_utc.astimezone(local_timezone)
        delta = datetime.datetime.now(local_timezone) - update_at_local
        return int(delta.total_seconds())

    def open_issue(self):
        """Changes the state of issue to 'open'.
        """
        self.github_request.update(issue=self, state='open')
        self.state = 'open'

    def comment(self, body):
        """Adds a comment to the issue.

        :params body: body, content of the comment
        :returns: issue object
        :rtype: :class:`exreporter.stores.github.GithubIssue`
        """
        self.github_request.comment(issue=self, body=body)

        if self.state == 'closed':
            self.open_issue()
        return self


class GithubRequest(object):
    """This class objects are created with valid credentials.
    The objects have methods to create/update issues and to add comments on Github.

    Basic Usage:
      >>> from exreporter.stores.github import GithubCredentials, GithubRequest
      >>> gc = GithubCredentials(user="username", repo="repo name", auth_token="personla auth token")
      >>> gr = GithubRequest(credentials=gc)
      >>> gr.create(title="title", body="body", labels=['labels'])
    """

    def __init__(self, credentials):
        self.user = credentials.user
        self.repo = credentials.repo
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': 'token {}'.format(credentials.auth_token)
        })

    def create(self, title, body, labels):
        """Create an issue in Github.
        For JSON data returned by Github refer:
        https://developer.github.com/v3/issues/#create-an-issue

        :param title: title of the issue
        :param body: body of the issue
        :param labels: list of labels for the issue
        :returns: dict of JSON data returned by Github of newly created issue
        :rtype: `dict`

        """
        url = "https://api.github.com/repos/{}/{}/issues".format(
            self.user, self.repo)

        data = {
            'title': title,
            'body': body,
        }

        if labels:
            data.update({'labels': labels})

        response = self.session.post(url, json.dumps(data))

        assert response.status_code == 201
        return json.loads(response.content)

    def comment(self, issue, body):
        """Comment on existing issue on Github.
        For JSON data returned by Github refer:
        https://developer.github.com/v3/issues/comments/#create-a-comment

        :param issue: object of exisiting issue
        :param body: body of the comment
        :returns: dict of JSON data returned by Github of the new comment
        :rtype: `dict`

        """
        url = issue.comments_url
        data = {'body': body}

        response = self.session.post(url, json.dumps(data))
        assert response.status_code == 201

        return json.loads(response.content)

    def update(self, issue, **kwargs):
        """Update an existing issue on Github.
        For JSON data returned by Github refer:
        https://developer.github.com/v3/issues/#edit-an-issue

        :param issue: object existing issue
        :returns: dict of JSON data returned by Github.
        :rtype: `dict`

        """
        url = issue.url

        response = self.session.patch(url, json.dumps(kwargs))

        assert response.status_code == 200
        return json.loads(response.content)

    def search(self, q, state, labels):
        """Search for issues in Github.
        For JSON data returned by Github refer:
        https://developer.github.com/v3/search/#search-issues

        :param q: query string for search
        :param state: the states of the issue
        :param labels: labels of the issue
        :returns: dictionary of JSON data returned by Github
        :rtype: `dict`

        """
        # TODO: add support for search with labels
        labels = ['"{}"'.format(label) for label in labels]
        q = "'{}'+state:{}+label:{}".format(
            q, '+state:'.join(state.split(',')), ','.join(labels))
        sort = "updated"

        url = "https://api.github.com/search/"\
              "issues?q={}+repo:{}/{}&sort={}".format(
                  q, self.user, self.repo, sort)

        response = self.session.get(url)
        assert response.status_code == 200
        return json.loads(response.content)
