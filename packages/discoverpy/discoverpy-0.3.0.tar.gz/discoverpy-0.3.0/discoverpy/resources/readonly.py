"""Resources which do not support writes."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from . import exceptions

from . import base


class ReadOnlyResource(base.Resource):

    """A resource which only supports GET operations."""

    valid_methods = ('get',)

    def create(self, query, data):
        """create a single resource with new property values.

        Args:
            query (Query): Query object constructed from the request.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.

        Raises:
            MethodNotAllowed: Always. This resource is read only.
        """
        raise exceptions.MethodNotAllowed(valid_methods=self.valid_methods)

    def update(self, query, identifier, data):
        """Update a single resource with new property values.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.

        Raises:
            MethodNotAllowed: Always. This resource is read only.
        """
        raise exceptions.MethodNotAllowed(valid_methods=self.valid_methods)

    def delete(self, query, identifier):
        """Delete a single resource with a given identifier.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.
            query (mapping): Key value pairs which represent the query
                parameters given in a request.

        Raises:
            MethodNotAllowed: Always. This resource is read only.
        """
        raise exceptions.MethodNotAllowed(valid_methods=self.valid_methods)
