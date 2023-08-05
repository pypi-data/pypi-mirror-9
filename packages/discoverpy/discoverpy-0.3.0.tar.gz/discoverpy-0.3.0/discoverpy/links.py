"""Standard interface for the Links object."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import math
import re


PAGE_REGEX = re.compile(r'page=\d+')
PAGE_SIZE_REGEX = re.compile(r'page_size=\d+')


def assert_numeric(value):
    """Raise TypeError if the value is not an int."""
    try:

        int(value)

    except ValueError:

        raise TypeError('Can only operate on int.')


class Links(object):

    """HTTP LINK header generator."""

    @staticmethod
    def make_url(url, page, page_size):
        """Generate a LINK URL with the given values.

        Args:
            url (str): The URL of a request to modify.
            page (int): The page number to use.
            page_size (int): THe page size to use.

        Returns:
            str: The modified URL which contains the pagination query.
        """
        if '?' not in url:

            url = '{0}?'.format(url)

        if PAGE_REGEX.search(url):

            url = PAGE_REGEX.sub('page={0}'.format(page), url)

        else:

            url = '{0}&page={1}'.format(url, page)

        if PAGE_SIZE_REGEX.search(url):

            url = PAGE_SIZE_REGEX.sub('page_size={0}'.format(
                page_size,
            ), url)

        else:

            url = '{0}&page_size={1}'.format(url, page_size)

        return url.replace('?&', '?')

    @staticmethod
    def make_link(url, page, page_size, rel):
        """Generate a single LINK header with a given rel.

        Args:
            url (str): The URL of a request to modify.
            page (int): The page number to use.
            page_size (int): THe page size to use.
            rel (str): The LINK rel to use in the output.

        Returns:
            str: The LINK header.
        """
        url = Links.make_url(url, page, page_size)
        return '<{0}>; rel="{1}"'.format(url, rel)

    def __init__(self, url, page, page_size, total):
        """Initialize the Links object.

        Args:
            url (str): The URL to use when constructing LINK headers. This
                value may contain query parameters.
            page (int): The current page number starting with 1.
            page_size (int): The number of elements on each page.
            total (int): THe total number of elements in all pages.
        """
        self._url = self.make_url(url, page, page_size)
        self._page = page or 1
        self._page_size = page_size
        self._total = total

    @property
    def url(self):
        """Get the source URL."""
        return self._url

    @property
    def page(self):
        """Get the current page."""
        return self._page

    @property
    def page_size(self):
        """Get the size of each page."""
        return self._page_size

    @property
    def total(self):
        """Get the total elements accounted for."""
        return self._total

    def __len__(self):
        """Return the number of pages."""
        return math.ceil(self.total / self.page_size)

    def _numeric_operation(self, other):
        """Ensure the other value is an integer within range."""
        try:

            int(other)

        except ValueError:

            raise TypeError('Can only add Links and int.')

        if other < 1 or (self.page + other) > len(self):

            return False

        return True

    def __add__(self, other):
        """Return a new Links or None.

        Args:
            other (int): The number of pages to increment by.

        Raises:
            TypeError: If other is not an integer.

        Return:
            Links: The Links which represents that page. If the page is out of
                bounds the result will be None.
        """
        assert_numeric(other)

        new_page = self.page + other
        if new_page > len(self) or new_page < 1:

            return None

        return type(self)(
            url=self.url,
            page=new_page,
            page_size=self.page_size,
            total=self.total,
        )

    def __sub__(self, other):
        """Return a new Links or None.

        Args:
            other (int): The number of pages to decrement by.

        Raises:
            TypeError: If other is not an integer.

        Return:
            Links: The Links which represents that page. If the page is out of
                bounds the result will be None.
        """
        assert_numeric(other)

        new_page = self.page - other
        if new_page > len(self) or new_page < 1:

            return None

        return type(self)(
            url=self.url,
            page=new_page,
            page_size=self.page_size,
            total=self.total,
        )

    def __repr__(self):
        """Get the current LINK header."""
        return self.make_link(
            url=self.url,
            page=self.page,
            page_size=self.page_size,
            rel='self',
        )

    def __str__(self):
        """Get a string of LINK headers."""
        header = []
        header.append(self.make_link(
            url=self.url,
            page=1,
            page_size=self.page_size,
            rel='first',
        ))
        header.append(self.make_link(
            url=self.url,
            page=len(self),
            page_size=self.page_size,
            rel='last',
        ))
        if self + 1:

            header.append(self.make_link(
                url=self.url,
                page=self.page + 1,
                page_size=self.page_size,
                rel='next',
            ))

        if self - 1:

            header.append(self.make_link(
                url=self.url,
                page=self.page - 1,
                page_size=self.page_size,
                rel='prev',
            ))

        return ', '.join(header)

    def __iter__(self):
        """Iterate over all LINK URLs in the set.

        Note:
            Each element is a URL only. It does not contain the <> enclosure
            or the rel text.
        """
        current = type(self)(
            url=self.url,
            page=1,
            page_size=self.page_size,
            total=self.total,
        )

        while current:

            yield current.url

            current = current + 1
