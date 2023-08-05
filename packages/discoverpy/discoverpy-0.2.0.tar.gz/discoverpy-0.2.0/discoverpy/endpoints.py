"""Base endpoints which provide handler functionality."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from restpy.endpoints import base
from werkzeug import exceptions
from werkzeug.wrappers import Response

from . import pagination


class DiscoverEndpoint(base.Endpoint):

    """Endpoint which exposes an implementation of the Resource interface."""

    _instance_methods = ('get', 'put', 'delete', 'head')
    _collection_methods = ('get', 'post', 'head')

    def __init__(self, resource):
        """Initialize the endpoint with a resource implementation."""
        self._resource = resource

    def dispatch(self, request, **kwargs):
        """Dispatch the request based on discover metadata."""
        method = request.method.lower()
        valid_methods = (
            self._instance_methods
            if request.instance else
            self._collection_methods
        )
        if method not in valid_methods:

            raise exceptions.MethodNotAllowed(
                valid_methods=valid_methods,
            )

        return getattr(self, method)(request)

    def get(self, request):
        """Get an instance or return a paginated list."""
        if request.instance:

            return Response(
                self._resource.get(
                    query=request.query,
                    identifier=request.identifier,
                ),
                status=200,
                direct_passthrough=True,
            )

        query = request.query
        response_data, total = self._resource.load(query)
        links = pagination.PaginationLinks(
            url=request.url,
            page=query.page,
            page_size=query.page_size,
            total=total,
        )
        return Response(
            response_data,
            status=200,
            direct_passthrough=True,
            headers={
                "Link": repr(links),
                "Total-Count": total,
            },
        )

    def post(self, request):
        """Create a new resource and return it."""
        return Response(
            self._resource.create(request.query, request.payload),
            status=201,
            direct_passthrough=True,
        )

    def put(self, request):
        """Update a resource and return it."""
        return Response(
            self._resource.update(
                request.query,
                request.identifier,
                request.payload,
            ),
            status=200,
            direct_passthrough=True,
        )

    def delete(self, request):
        """Delete a resource."""
        self._resource.delete(request.query, request.identifier)
        return Response('', status=204)
