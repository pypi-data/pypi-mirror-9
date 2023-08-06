Configuration
=============

LIVEWATCH_EXTENSIONS
--------------------

If you want to use it with ``cache`` or ``django-celery`` or ``django-rq`` you have to update the ``LIVEWATCH_EXTENSIONS`` setting.

cache
`````

Make sure that you have a ``cache`` installed and configured.

.. code-block:: python

    # Example with cache support
    LIVEWATCH_EXTENSIONS = (
        'livewatch.extensions.cache:CacheExtension',
    )

django-celery
`````````````

Make sure that you have ``celery`` installed. You can use the ``celery`` extra target for that.

.. code-block:: bash

    $ pip install django-livewatch[celery]

.. code-block:: python

    # Example with celery support
    LIVEWATCH_EXTENSIONS = (
        'livewatch.extensions.rq:CeleryExtension',
    )

django-rq
`````````

Make sure that you have ``rq`` installed. You can use the ``rq`` extra target for that.

.. code-block:: bash

    $ pip install django-livewatch[rq]

.. code-block:: python

    # Example with rq support
    LIVEWATCH_EXTENSIONS = (
        'livewatch.extensions.rq:RqExtension',
    )

.. hint::

    If you use ``celery`` or ``rq``, you have to ensure that a ``cache`` is running!

For details on writing your own extensions, please see the :ref:`extending-livewatch` section.
