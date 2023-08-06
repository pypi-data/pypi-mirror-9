.. _extending-livewatch:

Extending Livewatch
===================

.. code-block:: python

    from livewatch.extensions.base import BaseExtension


    class FooExtension(BaseExtension):
        name = 'foo'

        def check_service(self, request):
            # check that service is running

If you use a task queue service like celery or rq you can inherit your custom class from the ``TaskExtension`` class

.. code-block:: python

    from livewatch.extensions.base import TaskExtension


    class BarExtension(TaskExtension):
        name = 'bar'

        def run_task(self):
            # check that execution of a task works
