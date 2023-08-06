=====
InfoSessions
=====

Forked from https://github.com/martinrusev/django-redis-sessions

.. image:: https://travis-ci.org/ernado/infosessions.svg?branch=master
    :target: https://travis-ci.org/ernado/infosessions


.. image:: https://badge.fury.io/py/django-infosessions.svg
    :target: http://badge.fury.io/py/django-infosessions
    

Quick start
-----------

1. Add "infosessions" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = (
        ...
        'infosessions',
    )

2. Configure django to use infosessions as session engine ::

    SESSION_ENGINE = 'infosessions.session'

3. Add middleware to capture session information ::

    MIDDLEWARE_CLASSES = (
    	...
    	'infosessions.middlewares.SessionSyncMiddleware',
    )

4. Run `python manage.py migrate infosessions` to create the models.
