from __future__ import absolute_import

import django_rq
from django.core.cache import cache
from django.utils import timezone

from .base import TaskExtension


def livewatch_update_task():
    return cache.set('livewatch_watchdog', timezone.now(), 2592000)


class RqExtension(TaskExtension):
    name = 'rq'

    def run_task(self):
        django_rq.enqueue(livewatch_update_task)
