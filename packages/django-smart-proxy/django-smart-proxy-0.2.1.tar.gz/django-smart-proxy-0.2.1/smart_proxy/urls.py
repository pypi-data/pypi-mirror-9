# -*- coding: utf-8 -*-

from django.conf.urls import include, patterns, url

from .views import SmartProxyView

urlpatterns = patterns('',
    url(r'^(?P<proxy_id>[^/]+)/',
        SmartProxyView.as_view(),
        name='django-smart-proxy'),
)
