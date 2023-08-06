from __future__ import absolute_import

from django.core.cache import cache
from django.utils import timezone

from celery import shared_task


@shared_task
def livewatch_update_task():
    return cache.set('livewatch_watchdog', timezone.now(), 2592000)
