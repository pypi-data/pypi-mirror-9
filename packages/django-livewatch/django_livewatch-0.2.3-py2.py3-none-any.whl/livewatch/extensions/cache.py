import logging

from django.core.cache import cache

from .base import BaseExtension

logger = logging.getLogger(__name__)


class CacheExtension(BaseExtension):
    name = 'cache'

    def check_service(self, request=None):
        key = 'livewatch_{0}'.format(self.name)
        cache.set(key, 'cache_activated', 2592000)

        cache_activated = cache.get(key) == 'cache_activated'
        cache.delete(key)

        return cache_activated
