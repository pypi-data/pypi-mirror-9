django-livewatch
================

.. image:: https://badge.fury.io/py/django-livewatch.png
    :target: http://badge.fury.io/py/django-livewatch

.. image:: https://travis-ci.org/moccu/django-livewatch.svg
    :target: https://travis-ci.org/moccu/django-livewatch

.. image:: https://coveralls.io/repos/moccu/django-livewatch/badge.svg?branch=master
  :target: https://coveralls.io/r/moccu/django-livewatch?branch=master

.. image:: https://readthedocs.org/projects/django-livewatch/badge/?version=latest
    :target: http://django-livewatch.readthedocs.org/en/latest/

livewatch.de integration for django projects.


Installation
============

* Install ``django-livewatch`` (or `download from PyPI <http://pypi.python.org/pypi/django-livewatch>`_):

.. code-block:: python

    pip install django-livewatch

* If you use ``livewatch`` with ``celery`` add it to ``INSTALLED_APPS`` in ``settings.py``:

.. code-block:: python

    INSTALLED_APPS = (
        # other apps
        'livewatch',
    )

* Include ``livewatch.urls`` in your ``urls.py``:

.. code-block:: python

    urlpatterns += patterns('',
        (r'^livewatch/', include('livewatch.urls')),
    )


Usage
=====

Before you can use django-livewatch, you have to install and configure it.

To integrate ``django-livewatch`` with `livewatch.de <http://www.livewatch.de/>`_ you can use the following URLs:

* /livewatch/

... if you're using the celery extension:

* /livewatch/celery/

... if you're using the rq extension:

* /livewatch/rq/


Resources
=========

* `Documentation <https://django-livewatch.readthedocs.org/>`_
* `Bug Tracker <https://github.com/moccu/django-livewatch/issues>`_
* `Code <https://github.com/moccu/django-livewatch/>`_
