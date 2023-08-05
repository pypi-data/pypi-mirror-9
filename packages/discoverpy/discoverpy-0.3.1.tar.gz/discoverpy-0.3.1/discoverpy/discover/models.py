"""Discover service models."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

import json

import sqlalchemy
from sqlalchemy import schema
from sqlalchemy import types
from sqlalchemy.ext import declarative
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import scoping

from ..resources import sqlalchemy as sqlresource

ENGINE = sqlalchemy.create_engine('sqlite://')
SESSION = scoping.scoped_session(sessionmaker(bind=ENGINE))

BASE = declarative.declarative_base(cls=sqlresource.SqlalchemyDeclarativeMixin)


class Service(BASE):

    """A service in the registry."""

    __tablename__ = 'discover_service'

    name = schema.Column(types.String, primary_key=True)
    version = schema.Column(types.String, primary_key=True)
    description = schema.Column(types.Text)

    @classmethod
    def identifier(cls):
        """Use the service name in the url."""
        return cls.name


class Resource(BASE):

    """A resource in the registry."""

    __tablename__ = 'discover_resource'

    service = schema.Column(types.String, primary_key=True)
    version = schema.Column(types.String, primary_key=True)
    name = schema.Column(types.String, primary_key=True)
    description = schema.Column(types.Text)
    load = schema.Column(types.Text, nullable=True)
    get = schema.Column(types.Text, nullable=True)
    create = schema.Column(types.Text, nullable=True)
    update = schema.Column(types.Text, nullable=True)
    delete = schema.Column(types.Text, nullable=True)

    __table_args_ = (
        schema.ForeignKeyConstraint(
            (service, version),
            (Service.name, Service.version),
            name='fk_service',
        ),
    )

    @classmethod
    def property_map(cls):
        """Return a mapping of query names and columns."""
        return {
            "name": "name",
            "description": "description",
            "service": "service",
            "version": "version",
        }

    def to_dict(self):
        """Get a dictionary view of the data."""
        return {
            "service": self.service,
            "version": self.version,
            "name": self.name,
            "description": self.description,
            "load": json.loads(self.load) if self.load else None,
            "get": json.loads(self.get) if self.get else None,
            "create": json.loads(self.create) if self.create else None,
            "update": json.loads(self.update) if self.update else None,
            "delete": json.loads(self.delete) if self.delete else None,
        }

    @classmethod
    def identifier(cls):
        """Use the resource name in the url."""
        return cls.name
