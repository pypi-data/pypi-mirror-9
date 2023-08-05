"""Resource client."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json
import re

try:
    from urllib import parse
except ImportError:
    import urlparse as parse

from .. import validator as validatorlib
from . import http


class ResourceInstance(http.HttpClient):

    """Representation of a single resource."""

    def __init__(self, endpoint, body, validator, headers=None):
        """Initialize the resource with a response body."""
        self._body = body
        self._validator = validator
        super(ResourceInstance, self).__init__(endpoint, headers)

    @property
    def body(self):
        """Get the raw body."""
        return self._body

    @property
    def validator(self):
        """Get the resource validator."""
        return self._validator

    def get(self):
        """Fetch the most recent values."""
        self._body = super(ResourceInstance, self).get().json()

    def update(self, body):
        """Update with new values."""
        self.validator.update(body)
        self._body = self.put(data=json.dumps(body)).json()

    def delete(self):
        """Delete the resource."""
        super(ResourceInstance, self).delete()

    def __getattr__(self, name):
        """Lookup attributes in the response body."""
        if name in self.body:

            return self.body[name]

        raise AttributeError()

    def __repr__(self):
        """Get a view of the resource."""
        return str(self.body)


class ResourceManager(http.HttpClient):

    """HTTP client mixin which supports resource actions."""

    def __init__(
            self,
            endpoint,
            service,
            version,
            name,
            description,
            validator=None,
            headers=None,
    ):
        """Initialize the client with service data.

        Keyword Arguments:
            service (str): The service name.
            version (str): The service version.
            name (str): The resource name.
            description (str): The resource description.
            load: The validator schema for load.
            get: The validator schema for get.
            create: The validator schema for create.
            update: The validator schema for update.
            delete: The validator schema for delete.
        """
        self._service = service
        self._version = version
        self._name = name
        self._description = description
        self._validator = validator or validatorlib.Validator()
        super(ResourceManager, self).__init__(endpoint, headers)
        self._resource_url = parse.urljoin(self.endpoint, '{0}')

    @property
    def service(self):
        """Get the service within which the resource resides."""
        return self._service

    @property
    def version(self):
        """Get the version of the resource service."""
        return self._version

    @property
    def name(self):
        """Get the resource name."""
        return self._name

    @property
    def description(self):
        """Get the resource description."""
        return self._description

    @property
    def validator(self):
        """Get the resource validator."""
        return self._validator

    def get(self, identifier, query=None):
        """Get an instance of a resource.

        Args:
            identifier: The unique resource identifier.
            query (mapping): A mapping of query parameters.

        Return:
            ResourceInstance: An instance of the requested resource.
        """
        query = query or {}
        self.validator.get(query)
        response = self.request(
            self._resource_url.format(identifier),
            method='get',
            params=query,
        )
        body = response.json()
        return ResourceInstance(
            endpoint=body['href'],
            body=body,
            validator=self.validator,
            headers=self.headers,
        )

    def load(self, query=None):
        """Load an iterable of resources.

        Args:
            query (mapping): A mapping of query parameters.

        Return:
            iter of ResourceInstance: An iterable of ResourceInstance which
                match the given query.
        """
        query = query or {}
        self.validator.load(query)
        response = super(ResourceManager, self).get(params=query)
        resources = response.json()
        while resources:

            for resource in resources:

                yield ResourceInstance(
                    endpoint=resource['href'],
                    body=resource,
                    validator=self.validator,
                    headers=self.headers,
                )

            pages = response.headers['link'].split(', ')
            next_page_pattern = r'<(.*)>; rel="next"'
            next_page = None
            for page in pages:

                match = re.match(next_page_pattern, page)
                if match:

                    next_page = match.group(1)
                    break

            else:

                raise StopIteration()

            resources = None
            response = self.request(next_page, method='get')
            if response.status_code == 200:

                resources = response.json()

    def create(self, query=None, data=None):
        """Create a new instance of a resource.

        Args:
            query (mapping): A mapping of query parameters.
            data (mapping): A mapping of values to POST.

        Return:
            ResourceInstance: The newly created resource.
        """
        query = query or {}
        data = data or {}
        request_body = query.copy()
        request_body.update(data)
        self.validator.create(request_body)
        response = super(ResourceManager, self).post(
            params=query,
            data=json.dumps(data)
        )
        body = response.json()
        return ResourceInstance(
            endpoint=body['href'],
            body=body,
            validator=self.validator,
            headers=self.headers,
        )

    def update(self, identifier, query=None, data=None):
        """Get an instance of a resource.

        Args:
            identifier: The unique resource identifier.
            query (mapping): A mapping of query parameters.
            data (mapping): The mapping of values to PUT.

        Return:
            ResourceInstance: The new resource representation.
        """
        query = query or {}
        data = data or {}
        request_body = query.copy()
        request_body.update(data)
        self.validator.create(request_body)
        response = self.request(
            url=self._resource_url.format(identifier),
            method='put',
            params=query,
            data=json.dumps(data),
        )
        body = response.json()
        return ResourceInstance(
            endpoint=body['href'],
            body=body,
            validator=self.validator,
            headers=self.headers,
        )

    def delete(self, identifier, query=None):
        """Delete and instance of the resource.

        Args:
            identifier: The unique resource identifier.
            query (mapping): A mapping of query parameters.

        Return:
            None
        """
        query = query or {}
        self.validator.delete(query)
        self.request(
            self._resource_url.format(identifier),
            method='delete',
            params=query,
        )

    def __repr__(self):
        """Get a view of the manager."""
        return '<ResourceManager service={0} version={1} resource={2}>'.format(
            self.service,
            self.version,
            self.name,
        )
