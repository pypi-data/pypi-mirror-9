from __future__ import absolute_import

import re
import logging

from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View

from .utils import get_extensions


logger = logging.getLogger(__name__)

KEY_RE = re.compile(r'^[a-f0-9]{32}$')


class LiveWatchView(View):

    def get(self, request, *args, **kwargs):
        extensions = get_extensions()

        services_failed = []
        service = kwargs.get('service', None)
        if service:
            if service not in extensions:
                return HttpResponseNotFound()

            if not extensions[service].check_service(request):
                services_failed.append(service)
        else:
            for service in extensions:
                if not extensions[service].check_service(request):
                    services_failed.append(service)

        if services_failed:
            return HttpResponseNotFound('Error {0}'.format(', '.join(sorted(services_failed))))

        if 'key' not in request.GET:
            return HttpResponse('Ok')

        if KEY_RE.match(request.GET['key']):
            return HttpResponse(request.GET['key'])

        return HttpResponseNotFound()
