=====================
django-logentry-admin
=====================

|travis-ci-status| |coverage-status| |pypi-status|

Add Django LogEntries the the Django admin site.

Allows to view all log entries in the admin.

Originally based on: `Django snippet 2484 <http://djangosnippets.org/snippets/2484/>`_


Installation
============

Install by using pip or easy_install::

  pip install django-logentry-admin

Or install from source::

    git clone git@github.com:yprez/django-logentry-admin.git
    cd django-logentry-admin
    python setup.py install

To add this application into your project, just add it to your
``INSTALLED_APPS`` setting::

    INSTALLED_APPS = (
        ...
        'logentry_admin',
    )


.. |travis-ci-status| image:: http://img.shields.io/travis/tweepy/tweepy/master.svg?style=flat
   :target: http://travis-ci.org/yprez/django-logentry-admin

.. |coverage-status| image:: https://img.shields.io/coveralls/yprez/django-logentry-admin.svg?branch=master
   :target: https://coveralls.io/r/yprez/django-logentry-admin?branch=coveralls

.. |pypi-status| image:: http://img.shields.io/pypi/v/django-logentry-admin.svg?style=flat
    :target: https://pypi.python.org/pypi/django-logentry-admin
