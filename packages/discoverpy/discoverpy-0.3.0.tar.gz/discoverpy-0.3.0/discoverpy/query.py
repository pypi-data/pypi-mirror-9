"""Standard interface for the Query and Param objects."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections
import itertools

from werkzeug import urls


ANY = object()
DEFAULT_PAGE_SIZE = 25

SingleParameter = collections.namedtuple('SingleParameter', ('field', 'value'))
MultiParameter = collections.namedtuple('MultiParameter', ('field', 'values'))
AnyParameter = collections.namedtuple('AnyParameter', ('field'))
SortParameter = collections.namedtuple(
    'SortParameter', ('field', 'descending'),
)


class Parameter(object):

    """A query parameter from a URL string."""

    @staticmethod
    def decode(value):
        """Decode any special tokens into Python objects."""
        test = str(value).upper()
        if test == '$ANY':

            return ANY

        if test == '$NONE':

            return None

        if test == '$TRUE':

            return True

        if test == '$FALSE':

            return False

        return value

    @staticmethod
    def encode(value):
        """Encode any special Python objects into tokens."""
        if value is ANY:

            return '$ANY'

        if value is None:

            return '$NONE'

        if value is True:

            return '$TRUE'

        if value is False:

            return '$FALSE'

        return str(value)

    def __new__(cls, field, value):
        """Generate the appropriate parameter type from input.

        Args:
            field (str): The field name from the query.
            value (str): The string value from the query.

        Returns:
            AnyParameter: If the $ANY special token is anywhere in the value.
            SingleParameter: If there is only one value.
            MultiParameter: If there are multiple values.
        """
        values = str(value).split(',')
        values = tuple(cls.decode(value) for value in values)
        if ANY in values:

            return AnyParameter(field=field)

        if len(values) == 1:

            return SingleParameter(field=field, value=values[0])

        return MultiParameter(field=field, values=values)

    @classmethod
    def to_string(cls, param):
        """Generate a query string snippet from a Parameter.

        Args:
            param: Some Parameter object.

        Returns:
            str: The query string snippet. Ex: id=1,2,3,$NONE
        """
        if isinstance(param, AnyParameter):

            return '{0}=$ANY'.format(
                urls.url_quote(param.field)
            )

        if isinstance(param, SingleParameter):

            return '{0}={1}'.format(param.field, cls.encode(param.value))

        if isinstance(param, MultiParameter):

            return '{0}={1}'.format(
                param.field,
                ','.join(tuple(cls.encode(value) for value in param.values)),
            )

    @classmethod
    def from_string(cls, string):
        """Generate a Parameter from a query string snippet.

        Args:
            string (str): The snippet of a URL which contains a query
                parameter. Ex: id=1,2,3,$NONE

        Raises:
            ValueError: If the string is not a query string.

        Returns:
            AnyParameter: If the $ANY special token is anywhere in the value.
            SingleParameter: If there is only one value.
            MultiParameter: If there are multiple values.
        """
        if string.count('=') > 1:

            raise ValueError('Invalid query parameter string')

        if string.startswith('?'):

            string = string[1:]

        field, value = string.split('=')
        return cls(field, value)

    @classmethod
    def from_dict(cls, mapping):
        """Generate an iterable of Parameter from a dictionary.

        Args:
            mapping (mapping): Some mapping of query parameter fields to
                values. All values should be iterables of values even if there
                is only one.

        Returns:
            iter of Parameter: An iterable of parameters from the mapping.
        """
        for field, values in mapping.items():

            for value in values:

                yield cls(field, value)


class Query(object):

    """A query string wrapper."""

    def __init__(self, params):
        """Initialize the Query with an iterable of Parameter."""
        self._params = tuple(params)

    @property
    def parameters(self):
        """Get an iterable of Parameter contained within the Query."""
        return self._params

    def find(self, name):
        """Find all contains Parameter with the given field name."""
        return (param for param in self.parameters if param.field == name)

    def fetch(self, name):
        """Get the first Parameter with the given field name or None."""
        results = tuple(self.find(name))
        if not results:

            return None

        return results[0]

    def first(self, name, default=None):
        """Get the first value of the first Parameter with the given field."""
        param = self.fetch(name)
        if not param:

            return default

        if isinstance(param, SingleParameter):

            return param.value

        if isinstance(param, MultiParameter):

            return param.values[0]

        if isinstance(param, AnyParameter):

            return ANY

        return default

    @property
    def page(self):
        """Get the requested page of a paginated query.

        This page number is 0 based and defaults to 0 if not page is given in
        the query.
        """
        try:

            return (int(self.first('page', default=1)) - 1) or 0

        except ValueError:

            return 0

    @property
    def page_size(self):
        """Get the requested page size of a paginated query."""
        try:

            return int(self.first('page_size', default=DEFAULT_PAGE_SIZE))

        except ValueError:

            return DEFAULT_PAGE_SIZE

    @property
    def sort(self):
        """Get an iterable of SortParameter from the request."""
        param = self.fetch('sort')
        if not param:

            return ()

        if isinstance(param, SingleParameter):

            descending = False
            field = param.value
            if field.startswith('-'):

                descending, field = True, field[1:]

            return (SortParameter(field=field, descending=descending),)

        if isinstance(param, MultiParameter):

            values = (field for field in param.values)
            values = (
                (field[1:], True)
                if field.startswith('-') else (field, False)
                for field in values
            )
            values = (
                SortParameter(field=field, descending=descending)
                for field, descending in values
            )
            return values

        return ()

    def append(self, param):
        """Generate a new Query which contains the new parameter."""
        return type(self)(
            itertools.chain(
                self.parameters,
                (param,),
            )
        )

    def extend(self, params):
        """Generate a new Query which contains multiple new parameters."""
        return type(self)(
            itertools.chain(
                self.parameters,
                params,
            )
        )

    def remove(self, param):
        """Generate a new Query which does not contain the given parameter.

        Args:
            param (str or Parameter): If param is a string it is assumed to be
                a name and all Parameter with that name in the field slot will
                be removed. If it is a Parameter then only that instance will
                be removed from the new Query.

        Returns:
            Query: The new Query object.
        """
        if (
                isinstance(param, SingleParameter) or
                isinstance(param, MultiParameter) or
                isinstance(param, AnyParameter)
        ):

            return type(self)(
                parameter
                for parameter in self.parameters
                if parameter is not param
            )

        return type(self)(
            parameter
            for parameter in self.parameters
            if parameter.field != param
        )

    def to_string(self):
        """Generate a URL query string based on the Query content."""
        strings = (Parameter.to_string(param) for param in self.parameters)
        strings = '&'.join(tuple(strings))
        return '?{0}'.format(strings)

    def __str__(self):
        """Get the query string represented by this Query object."""
        return self.to_string()

    def __repr__(self):
        """Get the query string represented by this Query object."""
        return self.to_string()

    @classmethod
    def from_string(cls, string):
        """Generate a Query from a given query string.

        Args:
            string (str): The URL containing a query string to parse.

        Returns:
            Query: The new Query object.
        """
        string = string[1:] if string.startswith('?') else string
        values = urls.url_decode(string, decode_keys=True)
        values = values.to_dict(flat=False)
        return cls(Parameter.from_dict(values))

    def __iter__(self):
        """Iterate over the contained query parameters."""
        return iter(self.parameters)
