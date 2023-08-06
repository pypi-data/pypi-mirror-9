.. _installation:

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
