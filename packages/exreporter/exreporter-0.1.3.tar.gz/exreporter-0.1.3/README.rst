=========================================
Exreporter: Report Internal Server Errors
=========================================

.. image:: https://badge.fury.io/py/exreporter.png
    :target: http://badge.fury.io/py/exreporter

.. image:: https://travis-ci.org/vedarthk/exreporter.png?branch=master
        :target: https://travis-ci.org/vedarthk/exreporter

Exreporter is an MIT Licensed library, written in Python to report internal server errors and exceptions in background applications to issue trackers such as Github.

This will help in reducing the dependency on error emails for internal server error notifications and to manage them in a single, right place. Reported issues contain everything a developer needs, debugging got a whole lot simpler.

Also it should be easy to use:

.. code-block:: python

    from exreporter.credentials import GithubCredentials
    from exreporter.stores import GithubStore
    from exreporter import ExReporter
    gc = GithubCredentials(user="username", repo="repo-name", auth_token="personal-token")
    gs = GithubStore(credentials=gc)
    reporter = ExReporter(store=gs, labels=['Bug'])

    reporter.report()


Features
--------

- Creates issues in issue trackers
- Aggregate same kind of issues
- Handle multiple occurrence


Usage
--------

Usage reference available at https://exreporter.readthedocs.org/en/latest/usage.html


Documentation
-------------

Documentation is available at https://exreporter.readthedocs.org/.


TODOS
-----

#. Add support for Bitbucket
