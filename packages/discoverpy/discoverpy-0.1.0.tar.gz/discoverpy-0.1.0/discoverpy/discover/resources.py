"""Resources which provide the service discovery endpoints."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug import exceptions

from ..resources import base


class ReadOnlyResource(base.Resource):

    """A resource which only supports GET operations."""

    valid_methods = ('get',)

    def create(self, data):
        """create a single resource with new property values.

        Args:
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.

        Raises:
            MethodNotAllowed: Always. This resource is read only.
        """
        raise exceptions.MethodNotAllowed(valid_methods=self.valid_methods)

    def update(self, identifier, data):
        """Update a single resource with new property values.

        Args:
            identifier (str): The string representation of the unique id.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.

        Raises:
            MethodNotAllowed: Always. This resource is read only.
        """
        raise exceptions.MethodNotAllowed(valid_methods=self.valid_methods)

    def delete(self, identifier, query):
        """Delete a single resource with a given identifier.

        Args:
            identifier (str): The string representation of the unique id.
            query (mapping): Key value pairs which represent the query
                parameters given in a request.

        Raises:
            MethodNotAllowed: Always. This resource is read only.
        """
        raise exceptions.MethodNotAllowed(valid_methods=self.valid_methods)


class ServiceResource(ReadOnlyResource):

    """A resource which provides service listings."""

    def __init__(self, name, description, validator=None, services=()):
        """Initialize the resource with an iterable of services.

        Args:
            services (iter of Service): An iterable of Service objects which
                contain Resources.
        """
        super(ServiceResource, self).__init__(
            name,
            description,
            validator=validator,
        )
        self._services = tuple(services)
        self._service_map = dict(
            ((service.name, service.version), service) for service in services
        )

    def load(self, page, page_size, query):
        """Fetch an iterable of resources based on the given keyword arguments.

        Args:
            page (int): The page number to fetch.
            page_size (int): The number of items per page.
            query (mapping): Key value pairs which represent the query
                parameters given in a request.
        Raises:
            BadRequest: If the page_size is too large to process.
            BadRequest: If any of the query parameters cannot be used or are of
                the wrong types.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        services = self._services
        if 'name' in query:

            services = (
                service for service in services
                if service.name == query.get('name')
            )

        if 'version' in query:

            version = query.get('version')
            version = version[1:] if version.startswith('v') else version
            services = (
                service for service in services
                if service.version == version
            )

        services = tuple(services)

        if page * page_size > len(services):

            return ()

        start, stop = page * page_size, (page + 1) * page_size

        return tuple(
            {
                "name": service.name,
                "version": service.version,
                "description": service.description,
            } for service in services[start:stop]
        )

    def get(self, identifier, query):
        """Fetch a single resource based on some unique identifier.

        Args:
            identifier (str): The string representation of the unique id.
            query (mapping): Key value pairs which represent the query
                parameters given in a request.

        Raises:
            NotFound: If the resource does not exist.
            Gone: If the resource used to exist but no longer does.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        version = query.get('version')
        version = version[1:] if version.startswith('v') else version
        service = self._service_map.get((identifier, version))
        if not service:

            raise exceptions.NotFound(
                'The service with name {0} and version {1} not found.'.format(
                    identifier,
                    version,
                )
            )

        return {
            "name": service.name,
            "version": service.version,
            "description": service.description,
        }


class ResourceResource(ServiceResource):

    """A resource which provides resource listings."""

    def load(self, page, page_size, query):
        """Fetch an iterable of resources based on the given keyword arguments.

        Args:
            page (int): The page number to fetch.
            page_size (int): The number of items per page.
            query (mapping): Key value pairs which represent the query
                parameters given in a request.
        Raises:
            BadRequest: If the page_size is too large to process.
            BadRequest: If any of the query parameters cannot be used or are of
                the wrong types.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        service_name, version = query.get('service'), query.get('version')
        version = version[1:] if version.startswith('v') else version

        service = self._service_map.get((service_name, version))
        if not service:

            raise exceptions.NotFound(
                'The service with name {0} and version {1} not found.'.format(
                    service_name,
                    version,
                )
            )

        resources = tuple(service)

        if page * page_size > len(resources):

            return ()

        start, stop = page * page_size, (page + 1) * page_size

        return tuple(
            {
                "name": resource.name,
                "description": resource.description,
                "get": resource.validator.get,
                "load": resource.validator.load,
                "create": resource.validator.create,
                "update": resource.validator.update,
                "delete": resource.validator.delete,
            } for resource in resources[start:stop]
        )

    def get(self, identifier, query):
        """Fetch a single resource based on some unique identifier.

        Args:
            identifier (str): The string representation of the unique id.
            query (mapping): Key value pairs which represent the query
                parameters given in a request.

        Raises:
            NotFound: If the resource does not exist.
            Gone: If the resource used to exist but no longer does.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        service_name, version = query.get('service'), query.get('version')
        version = version[1:] if version.startswith('v') else version

        service = self._service_map.get((service_name, version))
        if not service:

            raise exceptions.NotFound(
                'The service with name {0} and version {1} not found.'.format(
                    service_name,
                    version,
                )
            )

        resource = service.get(identifier)
        if not resource:

            raise exceptions.NotFound(
                'The resource {0} not found in service {1} version {2}'.format(
                    identifier,
                    service_name,
                    version,
                )
            )

        return {
            "name": resource.name,
            "description": resource.description,
            "get": resource.validator.get,
            "load": resource.validator.load,
            "create": resource.validator.create,
            "update": resource.validator.update,
            "delete": resource.validator.delete,
        }
