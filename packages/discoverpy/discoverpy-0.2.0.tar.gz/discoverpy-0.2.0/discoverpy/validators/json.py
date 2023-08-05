"""JSON validators driven by jsonschema."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

import jsonschema
import jsonschema.exceptions
import werkzeug.exceptions

from . import base


class JsonValidator(base.Validator):

    """A JSON schema validator."""

    content_type = 'application/json'

    @staticmethod
    def encode(value):
        """Encode a value as JSON."""
        return json.dumps(value)

    @staticmethod
    def decode(value):
        """Decode string value into an object which can be validated.

        Args:
            value (str): The string value which should be decoded into a Python
                object.

        Raises:
            BadRequest: If the value cannot be decoded.
        """
        try:

            return json.loads(value or '{}')

        except:

            raise werkzeug.exceptions.BadRequest(
                'Could not decode JSON value.'
            )

    @staticmethod
    def validate(values, schema):
        """Determine if a given value is valid according to a given schema.

        Args:
            value: The value to validate.
            schema: The schema to use in validation.

        Raises:
            BadRequest: If the value is not valid according to the schema.
        """
        try:

            jsonschema.validate(values, schema)

        except jsonschema.exceptions.ValidationError as exc:

            raise werkzeug.exceptions.BadRequest(
                exc.message,
            )

    @property
    def get(self):
        """Get the schema for get."""
        return self._get or {}

    @property
    def load(self):
        """Get the schema for load."""
        return self._load or {}

    @property
    def create(self):
        """Get the schema for create."""
        return self._create or {}

    @property
    def update(self):
        """Get the schema for update."""
        return self._update or {}

    @property
    def delete(self):
        """Get the schema for delete."""
        return self._delete or {}
