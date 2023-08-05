"""Pagination helpers."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import re


PAGE_REGEX = re.compile(r'page=\d+')
PAGE_SIZE_REGEX = re.compile(r'page_size=\d+')


class PaginationLinks(object):

    """Generate pagination LINK headers."""

    @staticmethod
    def link(url, page, page_size, rel):
        """Generate an individual link.

        Args:
            url (str): The URL to use in the LINK headers. This value may
                contain query parameters.
            page (int): The current page.
            page_size (int): The entries on each page.
            rel (str): The value to place in the 'rel' field. Ex: first, last.
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

        url = url.replace('?&', '?')

        return '<{0}>; rel="{1}"'.format(url, rel)

    def __init__(self, url, page, page_size, total):
        """Initialize the class with pagination data.

        Args:
            url (str): The URL to use in the LINK headers. This value may
                contain query parameters.
            page (int): The current page starting with 0.
            page_size (int): The entries on each page.
            total (int): The total record count in the set.
        """
        self._url = url
        self._page = page + 1
        self._page_size = page_size
        self._total = total
        self._pages = self._total // self._page_size
        self._last_page = self._pages or 1

    @property
    def first(self):
        """Get the LINK for the first page of the set."""
        return self.link(
            url=self._url,
            page=1,
            page_size=self._page_size,
            rel='first',
        )

    @property
    def last(self):
        """Get the LINK for the last page of the set."""
        return self.link(
            url=self._url,
            page=self._last_page,
            page_size=self._page_size,
            rel='last',
        )

    @property
    def next(self):
        """Get the next LINK in the set if it exists."""
        if (
                self._page < 1 or
                self._page + 1 > self._pages or
                self._total < 1
        ):

            return None

        return self.link(
            url=self._url,
            page=self._page + 1,
            page_size=self._page_size,
            rel='next',
        )

    @property
    def previous(self):
        """Get the previous LINK in the set if it exists."""
        if self._page < 2 or self._page > self._pages or self._total < 1:

            return None

        return self.link(
            url=self._url,
            page=self._page - 1,
            page_size=self._page_size,
            rel='prev',
        )

    def __iter__(self):
        """Get an iterable of all LINKs."""
        links = [self.first, self.last]
        if self.next:

            links.append(self.next)

        if self.previous:

            links.append(self.previous)

        return iter(links)

    def __repr__(self):
        """Get a string repr of the LINKs."""
        return ', '.join(tuple(self))
