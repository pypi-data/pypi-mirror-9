Django-cmstemplates is efficient templates-in-db implementation.

.. image:: https://travis-ci.org/asyncee/django-cmstemplates.svg?branch=master
    :target: https://travis-ci.org/asyncee/django-cmstemplates

.. image:: https://coveralls.io/repos/asyncee/django-cmstemplates/badge.png?branch=master
    :target: https://coveralls.io/r/asyncee/django-cmstemplates?branch=master

.. image:: https://pypip.in/download/django-cmstemplates/badge.svg
    :target: https://pypi.python.org/pypi/django-cmstemplates/
    :alt: Downloads

.. image:: https://pypip.in/version/django-cmstemplates/badge.svg?text=pypi
    :target: https://pypi.python.org/pypi/django-cmstemplates/
    :alt: Latest Version

.. image:: https://pypip.in/py_versions/django-cmstemplates/badge.svg
    :target: https://pypi.python.org/pypi/django-cmstemplates/
    :alt: Supported Python versions

.. image:: https://pypip.in/status/django-cmstemplates/badge.svg
    :target: https://pypi.python.org/pypi/django-cmstemplates/
    :alt: Development Status

.. image:: https://pypip.in/license/django-cmstemplates/badge.svg
    :target: https://pypi.python.org/pypi/django-cmstemplates/
    :alt: License


Application is aimed to support python 2.7, 3.3, 3.4 and django 1.7+.


Features
========

1. Template blocks can be edited in your admin
2. Django's cache machinery is actively used
3. Template group autocreation (if group is not exist)
4. Codemirror widget support
5. Ability to view template only for superuser, useful when editing
   in production.


Installation
============

1. Add ``cmstemplates`` to ``INSTALLED_APPS``
2. Run ``./manage.py migrate cmstemplates``
3. Go to admin and create new group template with name *test-group*
   You can skip this step for now, if you want template to be
   auto-created.
4. Add this group to your template with built-in django ``include`` tag::

    {% cms_group "test-group" %}

   If you skipped step three, then template group *test-group*
   will be created automatically.

5. Create some templates for this group in admin.
6. Refresh target site page and see your templates content.


Using codemirror widget
=======================

Add to your settings::

    CMSTEMPLATES_USE_CODEMIRROR = True

Install codemirror widget:

1. source env/bin/activate
2. pip install django-codemirror-widget
3. cd project_name/static/vendor
4. wget http://codemirror.net/codemirror.zip
5. unzip codemirror.zip
6. mv codemirror-4.2 codemirror
7. Add to settings::

    CODEMIRROR_PATH = 'vendor/codemirror'
    CODEMIRROR_THEME = 'default'
    CODEMIRROR_CONFIG = {'lineNumbers': True}


Final settings should look like this::

    # cmstemplates
    CMSTEMPLATES_USE_CODEMIRROR = True

    # codemirror
    CODEMIRROR_PATH = 'vendor/codemirror'
    CODEMIRROR_THEME = 'default'
    CODEMIRROR_CONFIG = {'lineNumbers': True}
