"""Containers for discoverable resources."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from ..validators import base


class Resource(object):

    """A resource exposed through a REST API.

    Resources are an interface for creating, reading, updating, and
    deleting some underlying data. It should be subclassed to provide
    generic functionality for some type of resource. For example, one resource
    implementation might provide the interface for SQLAlchemy ORM
    models while another for files on a file system.

    All methods may raise HTTP exceptions. Some common exception cases are
    documented with the methods. Exceptions related to input validation
    should most likely not be handled directly within a resource. Instead
    hooks, middleware, and validators should be considered for this purpose.
    """

    def __init__(self, name, description, validator=None):
        """Initialize the resource with metadata.

        Args:
            name (str): The name of the resource as it appears in the URI.
            description (str): A human description of what the resource
                provides.

        Keyword Args:
            validator: A validator object used for the resource.
        """
        self._name = name
        self._description = description
        self._validator = validator or base.NoValidation()

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
        """Get the validator used for the resource."""
        return self._validator

    def load(self, query):
        """Fetch an iterable of resources based on the given query.

        Args:
            query (Query): Query object constructed from the request.

        Raises:
            BadRequest: If the page_size is too large to process.
            BadRequest: If any of the query parameters cannot be used or are of
                the wrong types.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.

        Returns:
            tuple: A two-tuple where the first element is the content and the
                second is the total number of elements which match the query.
        """
        raise NotImplementedError()

    def create(self, query, data):
        """create a single resource with new property values.

        Args:
            query (Query): Query object constructed from the request.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.

        Raises:
            BadRequest: If the data provided is malformed, insufficient, or
                invalid.
            Conflict: If the resource cannot be created because of some
                server side constraint.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        raise NotImplementedError()

    def get(self, query, identifier):
        """Fetch a single resource based on some unique identifier.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.

        Raises:
            NotFound: If the resource does not exist.
            Gone: If the resource used to exist but no longer does.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        raise NotImplementedError()

    def update(self, query, identifier, data):
        """Update a single resource with new property values.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.

        Raises:
            BadRequest: If the data provided is malformed, insufficient, or
                invalid.
            Conflict: If th resource cannot be updated because of some server
                side constraint.
            NotFound: If the resource does not exist.
            Gone: If the resource used to exist but no longer does.
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        raise NotImplementedError()

    def delete(self, query, identifier):
        """Delete a single resource with a given identifier.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.

        Raises:
            Unauthorized: If the requestor is not authenticated.
            Forbidden: If the requestor is not authorized to complete this
                action even with authentication.
        """
        raise NotImplementedError()
