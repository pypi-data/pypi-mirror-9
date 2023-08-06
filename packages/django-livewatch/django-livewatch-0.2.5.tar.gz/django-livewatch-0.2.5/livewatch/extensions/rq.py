from __future__ import absolute_import

import django_rq
from django.core.cache import cache
from django.utils import timezone

from .base import TaskExtension


def livewatch_update_rq_task(key):
    return cache.set(key, timezone.now(), 2592000)


class RqExtension(TaskExtension):
    name = 'rq'

    def run_task(self):
        key = 'livewatch_{0}'.format(self.name)
        django_rq.enqueue(livewatch_update_rq_task, key)
