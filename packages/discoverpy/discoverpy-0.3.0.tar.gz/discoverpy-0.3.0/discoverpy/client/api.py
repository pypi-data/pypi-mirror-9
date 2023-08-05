"""Client API driven by the requests library."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

try:
    from urllib import parse
except ImportError:
    import urlparse as parse

from .. import validator as validatorlib
from . import http
from . import resource as resourcelib


class ServiceClient(http.HttpClient):

    """Client for producing ResourceManager."""

    def __init__(self, endpoint, name, version, headers=None):

        super(ServiceClient, self).__init__(endpoint, headers)
        self._name = name
        self._version = version
        self._resource_manager = resourcelib.ResourceManager(
            endpoint=parse.urljoin(
                self.endpoint,
                'discover/v1/resource',
            ),
            service='discover',
            version='1',
            name='resource',
            description='',
            headers=self.headers,
        )

    @property
    def name(self):
        """Get the service name."""
        return self._name

    @property
    def version(self):
        """Get the service version."""
        return self._version

    @property
    def resources(self):
        """Get an iterable of ResourceManager."""
        endpoint = parse.urljoin(
            self.endpoint,
            '{0}/{1}'.format(self.name, self.version),
        )
        for res in self._resource_manager.load(
                query={"service": self.name, "version": self.version},
        ):

            yield resourcelib.ResourceManager(
                endpoint=parse.urljoin(endpoint, res.name),
                service=self.name,
                version=self.version,
                name=res.name,
                description=res.description,
                headers=self.headers,
                validator=validatorlib.Validator(
                    get=res.get,
                    load=res.load,
                    create=res.create,
                    update=res.update,
                    delete=res.delete,
                ),
            )

    def resource(self, name):
        """Get a ResourceManager for the given resource."""
        res = self._resource_manager.get(
            identifier=name,
            query={"service": self.name, "version": self.version},
        )
        endpoint = parse.urljoin(
            self.endpoint,
            '{0}/{1}'.format(self.name, self.version),
        ) + '/'
        return resourcelib.ResourceManager(
            endpoint=parse.urljoin(endpoint, res.name),
            service=self.name,
            version=self.version,
            name=res.name,
            description=res.description,
            headers=self.headers,
            validator=validatorlib.Validator(
                get=res.body['get'],
                load=res.body['load'],
                create=res.body['create'],
                update=res.body['update'],
                delete=res.body['delete'],
            ),
        )


class Client(http.HttpClient):

    """Client for any discover service."""

    def __init__(self, endpoint, headers=None):
        super(Client, self).__init__(endpoint, headers)
        self._endpoint = endpoint
        self._headers = headers or {}
        self._service_manager = resourcelib.ResourceManager(
            endpoint=parse.urljoin(
                self.endpoint,
                'discover/v1/service',
            ),
            service='discover',
            version='1',
            name='service',
            description='',
            headers=self.headers
        )

    @property
    def services(self):
        """Get an iterable of service clients."""
        for serv in self._service_manager.load():

            yield ServiceClient(
                endpoint=self.endpoint,
                name=serv.name,
                version=serv.version,
                headers=self.headers,
            )

    def service(self, name, version):
        """Fetch a service client by the given name and version."""
        serv = self._service_manager.get(
            identifier=name,
            query={"version": version},
        )
        return ServiceClient(
            endpoint=self.endpoint,
            name=serv.name,
            version=serv.version,
            headers=self.headers,
        )
