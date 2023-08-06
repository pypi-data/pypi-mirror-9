from __future__ import absolute_import

from django.conf.urls import url

from .views import LiveWatchView


urlpatterns = [
    url(r'^$', LiveWatchView.as_view(), name='livewatch'),
    url(r'^(?P<service>\w+)/$', LiveWatchView.as_view(), name='livewatch-service'),
]
