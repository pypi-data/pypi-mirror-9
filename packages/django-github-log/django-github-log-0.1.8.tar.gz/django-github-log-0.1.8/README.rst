django-github-log
=================

Create an issue group by error on github when django raises error

Installation
------------

Add following settings dictionary in your settings.py (LABELS is
optional)

.. code:: python

    GITHUB_LOG_SETTINGS = {
        'USER': 'REPOSITORY-OWNER',
        'REPO': 'REPOSITORY-NAME',
        'TOKEN': 'GITHUB-API-TOKEN',
        'LABELS': [
            'priority:normal',
            'type:error',
            ...
        ]
    }

Add "github\_log" in INSTALLED\_APPS

Add logging handler in settings.Logging['handlers']

.. code:: python

    'github': {
        'level': 'ERROR',
        'class': 'github_log.log.GitHubIssueHandler'
    },

Finally, ``python manage.py syncdb``
