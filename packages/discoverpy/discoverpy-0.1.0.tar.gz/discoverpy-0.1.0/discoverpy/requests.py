"""Request subclasses which provide discover data."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from werkzeug import exceptions
from werkzeug import utils
from werkzeug import wrappers


class DiscoverRequest(wrappers.Request):

    """Request subclass which adds discover data."""

    def __init__(self, *args, **kwargs):
        """Initialize the request with a service map.

        Keyword Args:
            service_map (mapping): A key value mapping where keys are
                combined service name and version and the values are service
                objects.
        """
        self._service_map = kwargs.pop('service_map', {})
        super(DiscoverRequest, self).__init__(*args, **kwargs)

    @utils.cached_property
    def parts(self):
        """Get the parts of the request path."""
        path = (
            self.path[1:] if self.path.startswith('/') else self.path
        )
        path = path[:-1] if path.endswith('/') else path
        return path.split('/')

    @property
    def service_name(self):
        """Get the name of the requested service."""
        return self.parts[0]

    @property
    def version(self):
        """Get the requested service version."""
        version = self.parts[1]
        version = version[1:] if version.startswith('v') else version
        return version

    @property
    def resource_name(self):
        """Get the requested resource name."""
        return self.parts[2]

    @property
    def identifier(self):
        """Get the resource identifier if present."""
        if len(self.parts) == 4:

            return self.parts[3]

        return None

    @property
    def service(self):
        """Get the service object associated with the request."""
        return self._service_map.get((self.service_name, self.version), None)

    @property
    def resource(self):
        """Get the resource object associated with the request."""
        if not self.service:

            return None

        return self.service.get(self.resource_name, None)

    @property
    def collection(self):
        """True if the request is directed at a collection else False."""
        return self.identifier is None

    @property
    def instance(self):
        """True if the request is directed at an instance else False."""
        return self.identifier is not None

    @property
    def resource_method(self):
        """Get the name of the resource method to call."""
        method = self.method.lower()
        if self.collection and method == 'get':

            return 'load'

        if self.instance and method == 'get':

            return 'get'

        if self.collection and method == 'post':

            return 'create'

        if self.instance and method == 'put':

            return 'update'

        if self.instance and method == 'delete':

            return 'delete'

        return None

    @utils.cached_property
    def payload(self):
        """Get the decoded request payload."""
        data = self.get_data()
        if data:

            return self.resource.validator.decode(data.decode())

        return {}

    @utils.cached_property
    def body(self):
        """Get the full request body for validation.

        If the decoded payload is a mapping it will be combined with the
        request query parameters. Payload values will overwrite query
        parameters in the event of a conflict.
        """
        query = self.args.to_dict()
        for param in query.keys():

            if len(query[param]) == 1:

                query[param] = query[param][0]

        payload = self.payload
        if hasattr(payload, '__getitem__'):

            query.update(payload)

        return query

    def validate(self):
        """Check if the request is a valid discover request.

        Raises:
            BadRequest: If the URL pattern of the request does not match one
                of the discover patterns
            NotFound: If the given service, version, or resource is not
                in the mapping for the request.
            BadRequest: If the request body does not validate against the
                resource validator.
        """
        if len(self.parts) < 3 or len(self.parts) > 4:

            raise exceptions.BadRequest(
                'Requests must match either /{service}/{version}/{resource} '
                'or /{service}/{version}/{resource}/{identifier}.'
            )

        if not self.service:

            raise exceptions.NotFound(
                'No service by the name of {0} at version {1}'.format(
                    self.service_name,
                    self.version,
                )
            )

        if not self.resource:

            raise exceptions.NotFound(
                'No resource by the name of {0} in the service {1}'.format(
                    self.resource_name,
                    self.service_name,
                )
            )

        if self.resource_method:

            getattr(self.resource.validator, 'validate_{0}'.format(
                self.resource_method,
            ))(self.body)
