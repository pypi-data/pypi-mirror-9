========
Usage
========

To use Exreporter in any project:

.. code-block:: python

    from exreporter import ExREporter
    from exreporter.credentials import GithubCredentials
    from exreporter.stores import GithubStore

    gc = GithubCredentials(
        user="username", repo="reponame", auth_token="personaltoken")
    gs = GithubStore(credentials=gc)
    reporter = ExREporter(store=gs)

    reporter.report()



Exreporter in Django Project
----------------------------

Exreporter requires following Django settings in ``settings.py``:

.. code-block:: python

    EXREPORTER_GITHUB_USER = "username"
    EXREPORTER_GITHUB_REPO = "reponame"
    EXREPORTER_GITHUB_AUTH_TOKEN = "personaltoken"
    EXREPORTER_GITHUB_LABELS = ['Bug']

And then add Exreporter's middleware in ``settings.py``:

.. code-block:: python

  MIDDLEWARE_CLASSES = (
      ...
      'exreporter.contrib.django_middlewares.ExreporterGithubMiddleware',
  )
