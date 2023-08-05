"""Standard interface for the Validator object."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import jsonschema
import jsonschema.exceptions
import werkzeug.exceptions


class Validator(object):

    """A JSON Schema validator."""

    @staticmethod
    def validate(data, schema):
        """Validate the given data against the given JSON schema.

        Args:
            data (mapping): A mapping of values to validate.
            schema (mapping): A mapping which represents a valid JSON schema.

        Raises:
            werkzeug.exceptions.BadRequest: If the data are not valid
                according to the schema.
        """
        try:

            jsonschema.validate(data, schema)

        except jsonschema.exceptions.ValidationError as exc:

            raise werkzeug.exceptions.BadRequest(
                exc.message,
            )

    def __init__(
            self,
            get=None,
            load=None,
            create=None,
            update=None,
            delete=None,
    ):
        """Initialize the validator with schema for resource methods."""
        self.get_schema = get or {}
        self.load_schema = load or {}
        self.create_schema = create or {}
        self.update_schema = update or {}
        self.delete_schema = delete or {}

    def get(self, data):
        """Validate a get request."""
        return self.validate(data, self.get_schema)

    def load(self, data):
        """Validate a load request."""
        return self.validate(data, self.load_schema)

    def create(self, data):
        """Validate a create request."""
        return self.validate(data, self.create_schema)

    def update(self, data):
        """Validate an update request."""
        return self.validate(data, self.update_schema)

    def delete(self, data):
        """Validate a delete request."""
        return self.validate(data, self.delete_schema)
