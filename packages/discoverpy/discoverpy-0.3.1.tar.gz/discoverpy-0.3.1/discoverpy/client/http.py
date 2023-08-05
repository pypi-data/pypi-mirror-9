"""HTTP client base."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import logging

import requests


LOG = logging.getLogger(__name__)


class HttpClient(object):

    """Simple HTTP client interface with GET/POST/PUT/DELETE support."""

    def __init__(self, endpoint, headers=None):
        """Initialize the client with an endpoint."""
        endpoint = endpoint + '/' if not endpoint.endswith('/') else endpoint
        self._endpoint = endpoint
        self._headers = headers or {}

    @property
    def endpoint(self):
        """Get the configured HTTP endpoint."""
        return self._endpoint

    @property
    def headers(self):
        """Get a copy of the fixed headers."""
        return self._headers.copy()

    def request(self, url, method, params=None, data=None, headers=None):
        """Execute an HTTP request.

        Args:
            url (str): The HTTP endpoint to hit.
            method (str): The HTTP method to use. Ex: GET/POST/PUT/DELETE
            params (mapping): Key value mapping of query parameters to include
                in the request.
            data (str): The data payload to send with the request.
            headers (mapping): Key value mapping of header values to include
                in the request.
        Returns:
            HttpResponse: A response wrapper object.
        """
        headers = headers.copy() if headers else {}
        headers.update(self.headers)
        LOG.debug(
            'Request: method=%s url=%s params=%s data=%s headers=%s',
            method,
            url,
            params,
            data,
            headers,
        )
        response = requests.request(
            method,
            url=url,
            params=params,
            data=data,
            headers=headers,
        )
        response.raise_for_status()
        return response

    def get(self, params=None, headers=None):
        """Execute a GET request against the stored endpoint.

        Args:
            params (mapping): Key value mapping of query parameters to include
                in the request.
            headers (mapping): Key value mapping of header values to include
                in the request.
        Returns:
            HttpResponse: A response wrapper object.
        """
        return self.request(
            self.endpoint,
            'get',
            params=params,
            headers=headers,
        )

    def post(self, params=None, data=None, headers=None):
        """Execute a POST request against the stored endpoint.

        Args:
            params (mapping): Key value mapping of query parameters to include
                in the request.
            data (str): The data payload to send with the request.
            headers (mapping): Key value mapping of header values to include
                in the request.
        Returns:
            HttpResponse: A response wrapper object.
        """
        return self.request(
            self.endpoint,
            'post',
            params=params,
            data=data,
            headers=headers,
        )

    def put(self, params=None, data=None, headers=None):
        """Execute a PUT request against the stored endpoint.

        Args:
            params (mapping): Key value mapping of query parameters to include
                in the request.
            data (str): The data payload to send with the request.
            headers (mapping): Key value mapping of header values to include
                in the request.
        Returns:
            HttpResponse: A response wrapper object.
        """
        return self.request(
            self.endpoint,
            'put',
            params=params,
            data=data,
            headers=headers,
        )

    def delete(self, params=None, headers=None):
        """Execute a DELETE request against the stored endpoint.

        Args:
            params (mapping): Key value mapping of query parameters to include
                in the request.
            headers (mapping): Key value mapping of header values to include
                in the request.
        Returns:
            HttpResponse: A response wrapper object.
        """
        return self.request(
            self.endpoint,
            'delete',
            params=params,
            headers=headers,
        )
