"""Application implementations which use Resource based routing."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import functools

from restpy.applications import base
from werkzeug import exceptions

from . import endpoints
from . import requests
from .discover import service


class DiscoverApplication(base.BaseApplication):

    """Application which uses discover resources for routing."""

    def __init__(self, services=(), before=(), after=(), request=None):
        """Initialize the application with a Map router.

        Args:
            services (iter of Service): An iterable of Service objects which
                contain Resources.
            before (iter of callable): An iterable of callables which are
                considered request hooks. Each of these will be executed before
                the handler and will be given the current request object. If
                a before hook returns a new request object it will replace the
                current request for the rest of the session.
            after (iter of callable): An iterable of callables which are
                considered response hooks. Each of these will be executed after
                the handler and will be given both the request and response. If
                the hook returns a new response object it will replace the
                current response for the rest of the session.
        """
        self._service_map = dict(
            ((service.name, service.version), service) for service in services
        )
        discover_service = service.make_service(services)
        self._service_map[
            (discover_service.name, discover_service.version)
        ] = discover_service
        request = request or requests.DiscoverRequest
        request = functools.partial(request, service_map=self._service_map)
        super(DiscoverApplication, self).__init__(
            before,
            after,
            request=request,
        )

    def after(self, request, response):
        """Process the after hooks while injecting validator decoding."""
        if not isinstance(response, exceptions.HTTPException):

            response.set_data(
                request.resource.validator.encode(response.response)
            )
            response.content_type = request.resource.validator.content_type
        return super(DiscoverApplication, self).after(request, response)

    @staticmethod
    def route(request):
        """Get the endpoint for the requested resource."""
        request.validate()
        return endpoints.DiscoverEndpoint(request.resource), {}
