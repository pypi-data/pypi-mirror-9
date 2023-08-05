"""Resources which provide the service discovery endpoints."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

from ..resources import sqlalchemy
from .. import services as servlib
from ..validators import json as jsonvalidator
from . import models


def make_service(services=()):
    """Generate a Service object from an iterable of services."""
    service = servlib.Service(
        name='discover',
        version='1',
        description='A service for discovering available services.',
    )
    services = list(services)
    services.append(service)
    service.add(
        sqlalchemy.ReadOnlySqlalchemyResource(
            name='service',
            description='Get listings of available services.',
            model=models.Service,
            session=models.SESSION,
            validator=jsonvalidator.JsonValidator(
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
        )
    )
    service.add(
        sqlalchemy.ReadOnlySqlalchemyResource(
            name='resource',
            description='Get a listing of available resources for a service.',
            model=models.Resource,
            session=models.SESSION,
            validator=jsonvalidator.JsonValidator(
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
        )
    )

    session = models.SESSION()
    models.BASE.metadata.create_all(bind=models.ENGINE)
    for service in services:

        session.add(models.Service(
            name=service.name,
            version=service.version,
            description=service.description,
        ))

        for resource in service:

            session.add(models.Resource(
                name=resource.name,
                description=resource.description,
                service=service.name,
                version=service.version,
                load=json.dumps(resource.validator.load),
                get=json.dumps(resource.validator.get),
                create=json.dumps(resource.validator.create),
                update=json.dumps(resource.validator.update),
                delete=json.dumps(resource.validator.delete)
            ))

    return service
