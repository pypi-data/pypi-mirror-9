"""Resource implementations related to SQLAlchemy."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc
from werkzeug import exceptions

from .. import query as querylib
from . import base
from . import readonly


class SqlalchemyDeclarativeMixin(object):

    """A SQLAlchemy declarative base mixin.

    Subclasses of this mixin should be used in conjunction with the
    SqlalchemyResource.
    """

    @classmethod
    def identifier(cls):
        """Return the column which is associated with a resource identifier.

        The default implementation is to use the first defined primary key.
        """
        return cls.__mapper__.primary_key[0]

    @classmethod
    def property_map(cls):
        """Return a mapping of query names and columns.

        The key of the mapping equates to the query parameter of a request and
        the attribute name passed in a request payload. The value is a column
        name as it is assigned in the ORM model.

        The default implementation is to use the column names directly as
        parameters. Implement this method to provide a custom mapping.
        """
        return dict((key, key) for key in cls.__mapper__.columns.keys())

    def to_dict(self):
        """Convert the model into a Python dictionary.

        The default implementation of this method uses the property_map
        class method to generate the dictionary. Implement this method if
        to provide a custom dictionary representation.
        """
        result = {}
        for param, column in self.property_map().items():

            result[param] = getattr(self, column)

        return result


def filter_query(query, attr, values):
    """Add a query filter.

    Args:
        query (Query): The SQLAlchemy query object to base the filter on.
        attr (Column): The SQLAlchemy column object to filter on.
        values (iter): An iterable of values by which to filter.

    Returns:
        Query: The SQLAlchemy query object with additional filters.
    """
    if len(values) > 1:

        values = tuple(value for value in values if value is not querylib.ANY)
        return query.filter(attr.in_(values))

    value = values[0]
    if value is None:

        return query.filter(attr.is_(None))

    if value is querylib.ANY:

        return query.filter(attr.isnot(None))

    return query.filter(attr == value)


def make_query(session, model, query):
    """Generate a query from a model and Query object.

    Args:
        session (Session): A SQLAlchemy session to use while querying.
        model (Base): The declarative base model to use while querying.
        query (Query): The Query object containing request query parameters.

    Returns:
        Query: A SQLAlchemy query object.
    """
    valid_params = model.property_map()
    model_query = session.query(model)
    query_params = (param for param in query if param.field in valid_params)
    for param in query_params:

        model_query = filter_query(
            model_query,
            getattr(model, valid_params.get(param.field)),
            param.values,
        )

    sorts = (sort for sort in query.sort if sort.field in valid_params)
    sorts = ((valid_params.get(sort.field), sort.descending) for sort in sorts)
    sorts = ((getattr(model, attr), descending) for attr, descending in sorts)
    sorts = (attr if descending else attr.desc() for attr, descending in sorts)
    model_query = model_query.order_by(*sorts)

    return model_query


def make_instance_query(session, model, query, identifier):
    """Generate instance query from model and Query object.

    Args:
        session (Session): A SQLAlchemy session to use while querying.
        model (Base): The declarative base model to use while querying.
        query (Query): The Query object containing request query parameters.
        identifier: The unique resource identifier to use while querying.

    Returns:
        Query: A SQLAlchemy query object.
    """
    return make_query(session, model, query).filter(
        model.identifier() == identifier
    )


class SqlalchemyResource(base.Resource):

    """A resource which is backed by a sqlalchemy ORM model.

    Models must either subclass the SqlalchemyDeclarativeMixin or implement
    the methods defined in that mixin.
    """

    def __init__(
            self,
            name,
            description,
            model,
            session,
            validator=None,
    ):
        """Initialize the resource with metadata.

        Args:
            name (str): The name of the resource as it should appear in the
                URI.
            description (str): A human description of what the resource
                represents.
            model (base.Model): A SQLAlchemy ORM model. Models are assumed to
                extend the SqlalchemyDeclarativeMixin.
            session: The SQLAlchemy session factory to use when querying.

        Keyword Args:
            validator: A validator object used for the resource.
        """
        super(SqlalchemyResource, self).__init__(
            name,
            description,
            validator=validator
        )
        self._model = model
        self._session = session
        self._properties = model.property_map()

    def _relevant_values(self, mapping):
        """Get a mapping of only the values in 'mapping' which are relevant.

        Relevant values are those which match up with those in 'properties'.
        """
        return dict(
            (key, value) for key, value in mapping.items()
            if key in self._properties
        )

    def load(self, query):
        """Fetch an iterable of resources based on the given keyword arguments.

        Args:
            query (Query): Query object constructed from the request.
        """
        model_query = make_query(self._session(), self._model, query)
        total = model_query.count()
        model_query = model_query.limit(query.page_size)
        model_query = model_query.offset(query.page_size * query.page)
        return tuple(instance.to_dict() for instance in model_query), total

    def create(self, query, data):
        """Create a single resource with new property values.

        Args:
            query (Query): Query object constructed from the request.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.
        """
        session = self._session()
        try:

            data = self._relevant_values(data)
            instance = self._model()
            for param, value in data.items():

                setattr(
                    instance,
                    self._properties.get(param),
                    value,
                )

            session.add(instance)
            session.commit()
            return instance.to_dict()

        except exc.IntegrityError:

            session.rollback()
            raise exceptions.BadRequest()

        except Exception as unknown_exc:

            session.rollback()
            raise unknown_exc

    def get(self, query, identifier):
        """Fetch a single resource based on some unique identifier.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.
        """
        try:

            return make_instance_query(
                self._session(),
                self._model,
                query,
                identifier,
            ).one().to_dict()

        except orm_exc.NoResultFound:

            raise exceptions.NotFound()

    def update(self, query, identifier, data):
        """Update a single resource with new property values.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.
        """
        session = self._session()
        try:

            instance = make_instance_query(
                session,
                self._model,
                query,
                identifier,
            ).one()

        except orm_exc.NoResultFound:

            raise exceptions.NotFound()

        try:

            for param, value in self._relevant_values(data).items():

                setattr(
                    instance,
                    self._properties.get(param),
                    value,
                )

            session.commit()

        except exc.IntegrityError:

            session.rollback()
            raise exceptions.BadRequest()

        return instance.to_dict()

    def delete(self, query, identifier):
        """Delete a single resource with a given identifier.

        Args:
            query (Query): Query object constructed from the request.
            identifier (str): The string representation of the unique id.
        """
        session = self._session()
        try:

            instance = make_instance_query(
                session,
                self._model,
                query,
                identifier,
            ).one()
            session.delete(instance)
            session.commit()

        except orm_exc.NoResultFound:

            pass

        except Exception as err:

            session.rollback()
            raise err


class ReadOnlySqlalchemyResource(
        readonly.ReadOnlyResource,
        SqlalchemyResource,
):

    """A SQLAlchemy resource which does not support writes."""

    pass
