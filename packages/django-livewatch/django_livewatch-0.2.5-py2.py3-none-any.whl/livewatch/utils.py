import importlib
import logging

from django.conf import settings


logger = logging.getLogger(__name__)


def get_extensions(reload_extensions=False):
    if not hasattr(get_extensions, '_cache') or reload_extensions:
        extensions = {}
        registered = getattr(settings, 'LIVEWATCH_EXTENSIONS', [])

        for extension in registered:
            try:
                base, cls = extension.split(':', 1)
                module = importlib.import_module(base)
                extension_class = getattr(module, cls)
                extensions[extension_class.name] = extension_class()
            except ImportError:
                logger.error('Failed to import {0}'.format(extension))

        get_extensions._cache = extensions

    return get_extensions._cache
