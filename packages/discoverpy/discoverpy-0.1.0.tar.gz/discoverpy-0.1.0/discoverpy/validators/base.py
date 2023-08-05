"""Validator interface and core implementations."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals


class Validator(object):

    """A request validator for a given resource.

    Implementations should raise BadRequest with an appropriate message if
    validation fails.

    Attributes:
        content_type (str): The content type which is associated with the
            decoded/encoded data.
    """

    content_type = 'text/plain'

    @staticmethod
    def encode(value):
        """Encode a value into the string format consumed by decode."""
        raise NotImplementedError()

    @staticmethod
    def decode(value):
        """Decode string value into an object which can be validated.

        Args:
            value (str): The string value which should be decoded into a Python
                object.

        Raises:
            BadRequest: If the value cannot be decoded.
        """
        raise NotImplementedError()

    @staticmethod
    def validate(value, schema):
        """Determine if a given value is valid according to a given schema.

        Args:
            value: The value to validate.
            schema: The schema to use in validation.

        Raises:
            BadRequest: If the value is not valid according to the schema.
        """
        raise NotImplementedError()

    def __init__(
            self,
            get=None,
            load=None,
            create=None,
            update=None,
            delete=None,
    ):
        """Initialize the validator with schema for different methods."""
        self._get = get
        self._load = load
        self._create = create
        self._update = update
        self._delete = delete

    @property
    def get(self):
        """Get the schema for get."""
        return self._get

    @property
    def load(self):
        """Get the schema for load."""
        return self._load

    @property
    def create(self):
        """Get the schema for create."""
        return self._create

    @property
    def update(self):
        """Get the schema for update."""
        return self._update

    @property
    def delete(self):
        """Get the schema for delete."""
        return self._delete

    def validate_get(self, value):
        """Validate the request for a 'get' resource method."""
        return self.validate(value, self.get)

    def validate_load(self, value):
        """Validate the request for a 'load' resource method."""
        return self.validate(value, self.load)

    def validate_create(self, value):
        """Validate the request for a 'create' resource method."""
        return self.validate(value, self.create)

    def validate_update(self, value):
        """Validate the request for an 'update' resource method."""
        return self.validate(value, self.update)

    def validate_delete(self, value):
        """Validate the request for a 'delete' resource method."""
        return self.validate(value, self.delete)


class NoValidation(Validator):

    """A validator which does nothing."""

    @staticmethod
    def encode(value):
        """Do nothing."""
        return value

    @staticmethod
    def decode(value):
        """Do nothing."""
        return value

    @staticmethod
    def validate(value, schema):
        """Do nothing."""
        return None
