"""Exceptions which can be raised by Resources."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class ResourceException(Exception):

    """Base exceptions for all exceptions thrown by resources."""

    pass


class NotFound(ResourceException):

    """The requested resource was not found."""

    pass


class Gone(ResourceException):

    """The request resource used to exist but is not gone."""

    pass


class Conflict(ResourceException):

    """Could not save the resource because of a conflict."""

    pass


class InvalidInput(ResourceException):

    """The resource method received invalid data."""

    pass


class Forbidden(ResourceException):

    """The requestor does is not authorized to execute the requested method."""

    pass


class MethodNotAllowed(ResourceException):

    """The requestor is not allowed to call this method."""

    def __init__(self, *args, **kwargs):
        """Initialize the exception with an iterable of valid methods.

        All instances of this exception must be given an iterable of valid
        resource methods which can be called.
        """
        self.valid_methods = kwargs.pop('valid_methods')
        super(MethodNotAllowed, self).__init__(*args, **kwargs)
