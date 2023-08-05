"""HTTP request endpoint which handles discover requests.."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

try:
    from urllib import parse
except ImportError:
    import urlparse as parse

from restpy.endpoints import base
from werkzeug import exceptions
from werkzeug.wrappers import Response

from .resources import exceptions as resource_exceptions
from . import links


def add_hrefs(root, path, query, identifier, items):
    """Add an href to each item in the items iterable."""
    for item in items:

        ident = str(item[identifier])
        href = parse.urljoin(root, path)
        href = parse.urljoin(href, ident)
        if query:

            href = '{0}?{1}'.format(href, query)

        item['href'] = href


class Endpoint(base.Endpoint):

    """Endpoint which exposes an implementation of the Resource interface."""

    _instance_methods = ('get', 'put', 'delete', 'head')
    _collection_methods = ('get', 'post', 'head')

    _instance_resource_methods = ('get', 'update', 'delete')
    _collection_resource_methods = ('load', 'create')

    _instance_method_map = dict(
        zip(_instance_resource_methods, _instance_methods)
    )
    _collection_method_map = dict(
        zip(
            _collection_resource_methods,
            _collection_methods
        )
    )

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

        try:

            return getattr(self, method)(request)

        except resource_exceptions.NotFound as exc:

            raise exceptions.NotFound(str(exc))

        except resource_exceptions.Gone as exc:

            raise exceptions.Gone(str(exc))

        except resource_exceptions.Conflict as exc:

            raise exceptions.Conflict(str(exc))

        except resource_exceptions.InvalidInput as exc:

            raise exceptions.BadRequest(str(exc))

        except resource_exceptions.Forbidden as exc:

            raise exceptions.Forbidden(str(exc))

        except resource_exceptions.MethodNotAllowed as exc:

            valid_methods = exc.valid_methods or ()
            method_map = self._collection_method_map
            if request.instance:

                method_map = self._instance_method_map

            valid_methods = [
                method_map.get(valid_method)
                for valid_method in valid_methods
            ]
            if 'get' in valid_methods:

                valid_methods.append('head')

            raise exceptions.MethodNotAllowed(
                str(exc),
                valid_methods=valid_methods,
            )

    def get(self, request):
        """Get an instance or return a paginated list."""
        if request.instance:

            instance = self._resource.get(
                query=request.query,
                identifier=request.identifier,
            )
            instance['href'] = request.url
            return Response(instance, status=200, direct_passthrough=True)

        query = request.query
        response_data, total = self._resource.load(query)
        link_headers = links.Links(
            url=request.url,
            page=query.page + 1,
            page_size=query.page_size,
            total=total,
        )
        add_hrefs(
            root=request.url_root,
            path=request.path,
            query=request.query_string.decode('utf8'),
            identifier=self._resource.identifier,
            items=response_data,
        )
        return Response(
            response_data,
            status=200,
            direct_passthrough=True,
            headers={
                "Link": str(link_headers),
                "Total-Count": total,
            },
        )

    def post(self, request):
        """Create a new resource and return it."""
        instance = self._resource.create(request.query, request.payload)
        instance['href'] = request.url
        return Response(instance, status=201, direct_passthrough=True)

    def put(self, request):
        """Update a resource and return it."""
        instance = self._resource.update(
            request.query,
            request.identifier,
            request.payload,
        )
        instance['href'] = request.url
        return Response(instance, status=200, direct_passthrough=True)

    def delete(self, request):
        """Delete a resource."""
        self._resource.delete(request.query, request.identifier)
        return Response('', status=204)
