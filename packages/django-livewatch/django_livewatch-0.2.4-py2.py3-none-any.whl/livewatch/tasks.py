from __future__ import absolute_import

from django.core.cache import cache
from django.utils import timezone

from celery import shared_task


@shared_task
def livewatch_update_celery_task(key):
    return cache.set(key, timezone.now(), 2592000)
