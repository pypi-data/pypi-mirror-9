"""Containers for versioned services."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class Service(object):

    """A service exposed by an API."""

    def __init__(self, name, description, version='1'):
        """Initialize the service with metadata.

        Args:
            name (str): The name of the service as it appears in the URI.
            description (str): A human description of what the service
                provides.
            version (str): The version string which identifies the iteration
                of the service.
        """
        self._name = name
        self._description = description
        self._version = version
        self._resources = {}

    @property
    def name(self):
        """Get the service name."""
        return self._name

    @property
    def description(self):
        """Get the service description."""
        return self._description

    @property
    def version(self):
        """Get the service version string."""
        return self._version

    def add(self, resource):
        """Add a resource to the service.

        Raises:
            ValueError: If a resource by this name already exists within the
                service.
        """
        if resource.name in self._resources:

            raise ValueError(
                'The resource {0} already exists in this service.'.format(
                    resource.name,
                )
            )

        self._resources[resource.name] = resource

    def get(self, name, default=None):
        """Get a resource from the service by name.

        Args:
            name (str): The name of the resource.
            default: The default value to return if not found.
        """
        return self._resources.get(name, default)

    def __iter__(self):
        """Iterate over the contained resources."""
        return iter(self._resources.values())
