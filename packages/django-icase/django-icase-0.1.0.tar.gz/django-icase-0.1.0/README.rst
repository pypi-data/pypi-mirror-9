=============================
django-icase
=============================

.. image:: https://badge.fury.io/py/django-icase.svg
    :target: https://badge.fury.io/py/django-icase

.. image:: https://travis-ci.org/bennylope/django-icase.svg?branch=master
    :target: https://travis-ci.org/bennylope/django-icase

.. image:: https://coveralls.io/repos/bennylope/django-icase/badge.svg?branch=master
    :target: https://coveralls.io/r/bennylope/django-icase?branch=master

A few tools for helping with case-insensitvity in Django URLs.

- 404 handler that redirects non-matched, non-lowercase URLs. E.g. if `/About/`
  is not matched, the handler will redirect to `/about/` before returning a 404
- Middleware that enforces lower-cased URLs. E.g. all non-lowercased URLs will
  be redirected to their lowercased form.

Overview
--------

If you only need to match URL patterns, then it's simple to add
case-insensitivity to your regular expressions.::

    urlpatterns = patterns('',
        (r'^(?i)admin/(.*)', admin.site.root),
        (r'^(?i)static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.STATIC_DOC_ROOT, 'show_indexes': True}),
        (r'^(?i)login/$', 'django.contrib.auth.views.login'),
        (r'^(?i)logout/$', do_logout),
    )

From Alex Martelli's `Stack Overflow explanation <http://stackoverflow.com/a/1515657/122291>`_.

However this doesn't do anything to match slugs, which are often case-sensitive
matched by default - it's up to the app. If the app uses a straightforward `=`
expression, e.g.::

    object = MyModel.objects.get(slug=slug)

Then `MySlug` won't match `myslug`.

There are also instances where you want to enforce URL casing for other reasons
(or a client does!).

Installation
------------

Install django-icase::

    pip install django-icase

To use the custom 404 handler, simply specify this in your project `urls.py`
configuration.::

    handler404 = 'icase.views.icase_404_handler'

To use the lowercasing middleware, add it to your
`INSTALLED_MIDDLEWARE`.::

    INSTALLED_MIDDLEWARE = (
        'icase.middleware.LowerCased',
        ...
    )

Django & Python support
-----------------------

Actively supported versions of Django are supported by this app,
although there is little reason it should not work on others.

Tested against Python 3 and Python 2.7.9.
