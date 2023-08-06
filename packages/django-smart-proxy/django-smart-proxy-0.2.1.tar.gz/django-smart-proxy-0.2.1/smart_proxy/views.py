# -*- coding: utf-8 -*-

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import logging
import re

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.core.validators import URLValidator
from django.http import Http404, HttpResponseBadRequest
from django.utils.module_loading import import_by_path
from django.views.generic import View

from .models import SmartProxyRequest

SMART_PROXIES = getattr(settings, 'SMART_PROXIES', {})
"""Global configuration for all Smart Proxies."""

logger = logging.getLogger(__name__)


class SmartProxyView(View):
    """
    The View where all the magic happens.
    """

    proxy_id = None
    """
    A string identifier representing this proxy.
    This is used as the URL prefix for the proxy.
    """

    proxy_settings = {}
    """Convenient class-level cache of PROXY_SETTINGS dict."""

    allowed_methods = SmartProxyRequest.HTTP_METHODS
    """
    An iterable containing the case-insensitive HTTP verbs that this proxy
    can support.
    """

    host_endpoint = ''
    """The base URL to which this proxy will forward all requests."""

    timeout = 60.0
    """The timeout, in seconds, for requests to the host."""

    request_decorators = ()
    """
    An iterable of callables (these can be strings).
    These can be used to modify the URL and/or headers of a request to the
    host prior to sending.
    """

    validate = URLValidator()
    """Used to validate the configured host endpoints."""

    def dispatch(self, request, *args, **kwargs):
        """
        Determines the destination URL, validates it, records it, and
        dispatches the modified request to the appropriate handler.
        """

        # Load proxy settings
        self._load_proxy_settings()

        # Construct the full source request URL
        url = self._construct_destination_url(request)

        # Build and cache the SmartProxyRequest object
        kwargs['current_request'] = self._build_request(request, url)

        # Get the response from remote server and return
        try:
            response = super(SmartProxyView, self).dispatch(request,
                                                            *args,
                                                            **kwargs)
        except Exception as e:
            logger.exception(e)
            response = HttpResponseBadRequest(e)

        return response

    def get(self, request, *args, **kwargs):
        """Delegates request to `requests.get`."""
        return kwargs['current_request'].send('get')

    def put(self, request, *args, **kwargs):
        """Delegates request to `requests.put`."""
        return kwargs['current_request'].send('put')

    def post(self, request, *args, **kwargs):
        """Delegates request to `requests.post`."""
        return kwargs['current_request'].send('post')

    def delete(self, request, *args, **kwargs):
        """Delegates request to `requests.delete`."""
        return kwargs['current_request'].send('delete')

    def head(self, request, *args, **kwargs):
        """Delegates request to `requests.head`."""
        return kwargs['current_request'].send('head')

    def options(self, request, *args, **kwargs):
        """Delegates request to `requests.options`."""
        return kwargs['current_request'].send('options')

    def patch(self, request, *args, **kwargs):
        """Delegates request to `requests.patch`."""
        return kwargs['current_request'].send('patch')


    ###################
    # Utility Methods #
    ###################

    def _load_proxy_settings(self):
        """Initializes the View with settings from the PROXY_SETTINGS dict."""

        # Fetch settings for this proxy (if we haven't already).
        if not self.proxy_settings:
            self.proxy_id = self.kwargs.get('proxy_id', None)

            if self.proxy_id and self.proxy_id in SMART_PROXIES:
                self.proxy_settings = SMART_PROXIES[self.proxy_id]

                # Retrieve and validate the host endpoint.
                self.host_endpoint = self._get_host_endpoint()

                # Update allowed_methods in accordance with configuration
                if 'allowed_methods' in self.proxy_settings:
                    self.allowed_methods = self.proxy_settings['allowed_methods']

                # Update timeout in accordance with configuration
                if 'timeout' in self.proxy_settings:
                    self.timeout = self.proxy_settings['timeout']

                # Any request decorators defined?
                self.request_decorators = self._get_request_decorators()

            else:
                raise Http404('The specified Django Smart Proxy could not be found.')

    def _get_headers(self, request):
        # TODO: what to do here?
        return {}

    def _build_request(self, request, url):
        """Transforms a request into a SmartProxyRequest."""

        current_request = SmartProxyRequest(url=url,
                                            data=self.request.body,
                                            headers=self._get_headers(request),
                                            settings=self.proxy_settings,
                                            timeout=self.timeout)

        # Apply request decorators, if provided
        for decorator in self.request_decorators:
            try:
                current_request = decorator(current_request,
                                            session=request.session)
            except Exception as e:
                logger.exception(e)

        # Return the SmartProxyRequest object
        return current_request


    def _construct_destination_url(self, request):
        """
        Transforms the request URL into the equivalent URL at the host
        endpoint.
        """
        return re.sub(r'.*/{0}/(.*)'.format(self.proxy_id),
                      r'{0}\1'.format(self.host_endpoint),
                      request.get_full_path())

    def _get_request_decorators(self):
        """
        Checks to see if request decorators have been defined.
        If so, translates fully-qualified string representations to callables and
        populates self.request_decorators with the list of callables. If a request
        decorator cannot be resolved, a warning is logged, but we will continue
        gracefully.
        """

        request_decorators = self.request_decorators

        if 'request_decorators' in self.proxy_settings:
            for request_decorator in self.proxy_settings['request_decorators']:
                if not hasattr(request_decorator, '__call__'):
                    try:
                        request_decorator = import_by_path(request_decorator)
                    except ImproperlyConfigured as e:
                        logger.warning(e)
                        continue

                request_decorators += (request_decorator,)

        return request_decorators

    def _get_host_endpoint(self):
        """
        Checks that we've identified a host for the specified proxy, and that
        it's a valid URL.
        """

        host_endpoint = self.proxy_settings.get('host_endpoint',
                                                self.host_endpoint)

        # Is the host endpoint defined?
        if not host_endpoint:
            raise Http404('A host has not been configured for the specified '
                          'Django Smart Proxy.')

        # Is the host endpoint a valid URL?
        try:
            self.validate(host_endpoint)
        except ValidationError as e:
            raise HttpResponseBadRequest(e)

        # Host endpoint looks good -- return the valid url.
        return host_endpoint
