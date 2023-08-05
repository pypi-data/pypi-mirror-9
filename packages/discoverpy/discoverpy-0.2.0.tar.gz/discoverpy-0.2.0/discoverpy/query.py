"""Query param helpers."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import collections


ANY = object()
SortParam = collections.namedtuple('SortParam', ('field', 'descending'))
QueryParam = collections.namedtuple('QueryParam', ('field', 'values'))


class Query(object):

    """Query param parser."""

    @staticmethod
    def convert(value):
        """Convert special tokens to Python values.

        Args:
            value (str): The token to convert.

        If the value is not a special token it will not be changed.
        """
        test_value = value.upper()
        if test_value == '$ANY':

            return ANY

        if test_value == '$NONE':

            return None

        if test_value == '$TRUE':

            return True

        if test_value == '$FALSE':

            return False

        return value

    def __init__(self, params):
        """Initialize the query with a param mapping.

        Args:
            params (mapping): A mapping of query parameters. Values must be
                iterables of elements.

        The following keys are special and will be handled differently:

            -   page

                This will become the 'page' property of the Query.

            -   page_size

                This will become the 'page_size' property of the Query.

            -   sort

                This will become the 'sort' property of the Query.

        The following values are special and will be handled differently:

            -   $ANY

                This will be converted as a reference to the ANY object.

            -   $NONE

                This will be converted to None.

            -   $TRUE

                This will be converted to True.

            -   $FALSE

                This will be converted to False.
        """
        self._params = params
        self._sort = self._params.get('sort', None)

        try:

            self._page = int(self._params.get('page', (1,))[0]) or 1

        except ValueError:

            self._page = 1

        try:

            self._page_size = (
                int(self._params.get('page_size', (50,))[0]) or 50
            )

        except ValueError:

            self._page_size = 50

    @property
    def page(self):
        """Get the requested page."""
        return self._page - 1

    @property
    def page_size(self):
        """Get the requested page_size."""
        return self._page_size

    @property
    def sort(self):
        """Get an iterable of SortParam."""
        if not self._sort:

            raise StopIteration()

        for sort_param in self._sort[0].split(','):

            descending = False
            if sort_param.startswith('-'):

                descending = True
                sort_param = sort_param[1:]

            yield SortParam(field=sort_param, descending=descending)

    @property
    def parameters(self):
        """Get an iterable of QueryParam."""
        ignore = ('page', 'page_size', 'sort')
        for field, values_list in self._params.items():

            if field not in ignore:

                for values in values_list:

                    values = (
                        self.convert(value) for value in values.split(',')
                    )
                    yield QueryParam(field=field, values=tuple(values))

    def __iter__(self):
        """Iter over QueryParam."""
        return self.parameters
