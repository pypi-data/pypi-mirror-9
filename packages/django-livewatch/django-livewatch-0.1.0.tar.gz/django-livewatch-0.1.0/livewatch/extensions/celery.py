from __future__ import absolute_import

from .base import TaskExtension
from ..tasks import livewatch_update_task


class CeleryExtension(TaskExtension):
    name = 'celery'

    def run_task(self):
        livewatch_update_task.delay()
