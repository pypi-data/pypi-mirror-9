"""Resources which provide the service discovery endpoints."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from .. import services as servlib
from ..validators import json
from . import resources


def make_service(services=()):
    """Generate a Service object from an iterable of services."""
    service = servlib.Service(
        name='discover',
        version='1',
        description='A service for discovering available services.',
    )
    services = list(service)
    services.append(service)
    service.add(
        resources.ServiceResource(
            name='service',
            description='Get listings of available services.',
            validator=json.JsonValidator(
                load={
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "service_load",
                    "description": "service load query params",
                    "type": "object",
                    "properties": {
                        "name": {
                            "description": "Name of the service.",
                            "type": "string",
                        },
                        "version": {
                            "description": "Version of the service.",
                            "type": "string",
                            "pattern": r"^[v]?(\d+)(\.\d+)*$",
                        },
                    },
                },
                get={
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "service_get",
                    "description": "service get query params",
                    "type": "object",
                    "properties": {
                        "version": {
                            "description": "Version of the service.",
                            "type": "string",
                            "pattern": r"^[v]?(\d+)(\.\d+)*$",
                        },
                    },
                    "required": ["version"]
                },
            ),
            services=services,
        )
    )
    service.add(
        resources.ResourceResource(
            name='resource',
            description='Get a listing of available resources for a service.',
            validator=json.JsonValidator(
                load={
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "resource_load",
                    "description": "resource load query params",
                    "type": "object",
                    "properties": {
                        "service": {
                            "description": "Name of a service.",
                            "type": "string",
                        },
                        "version": {
                            "description": "Version of a service.",
                            "type": "string",
                            "pattern": r"^[v]?(\d+)(\.\d+)*$",
                        },
                    },
                    "required": ["service", "version"],
                },
                get={
                    "$schema": "http://json-schema.org/draft-04/schema#",
                    "title": "resource_load",
                    "description": "resource load query params",
                    "type": "object",
                    "properties": {
                        "service": {
                            "description": "Name of a service.",
                            "type": "string",
                        },
                        "version": {
                            "description": "Version of a service.",
                            "type": "string",
                            "pattern": r"^[v]?(\d+)(\.\d+)*$",
                        },
                    },
                    "required": ["service", "version"],
                },
            ),
            services=services,
        )
    )
    return service
