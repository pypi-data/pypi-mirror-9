"""Resource implementations related to SQLAlchemy."""

from __future__ import division
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

from sqlalchemy import exc
from sqlalchemy.orm import exc as orm_exc
from werkzeug import exceptions


class SqlalchemyDeclarativeMixin(object):

    """A SQLAlchemy declarative base mixin.

    Subclasses of this mixin should be used in conjunction with the
    SqlalchemyResource.
    """

    @classmethod
    def property_map(cls):
        """Return a mapping of query names and columns.

        The key of the mapping equates to the query parameter of a request and
        the attribute name passed in a request payload. The value is a column
        name as it is assigned in the ORM model.

        The default implementation is to use the column names directly as
        parameters. Implement this method to provide a custom mapping.
        """
        return dict((key, key) for key in cls.columns.keys())

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


class SqlalchemyResource(object):

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
            session: The SQLAlchemy session object to use when querying.

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

    def _filter(self, query, attr, param):
        """Generate a new query which filters on the given parameter value.

        Args:
            query: The query object to build from.
            attr (str): The name of the model attribute to filter on.
            param: The query parameter value.
        """
        attr = getattr(self._model, attr)
        param = param or None
        if hasattr(param, '__iter__'):

            return query.filter(attr.in_(param))

        return query.filter(attr == param)

    def load(self, page, page_size, query):
        """Fetch an iterable of resources based on the given keyword arguments.

        Args:
            page (int): The page number to fetch.
            page_size (int): The number of items per page.
            query: Key value pairs which represent the query parameters given
                in a request.

        Query parameter values are compared using == unless the value is a list
        in which case in_ is used instead. If a query parameter is given but
        has an empty value then the comparison will be to None.
        """
        model_query = self._session.query(self._model)
        for query_name in self._relevant_values(query):

            model_query = self._filter(
                model_query,
                self._properties.get(query_name),
                query.get(query_name),
            )

        total = model_query.count()
        model_query = model_query.limit(page_size).offset(page_size * page)
        return (instance.to_dict() for instance in model_query), total

    def create(self, data):
        """Create a single resource with new property values.

        Args:
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.
        """
        data = self._relevant_values(data)
        instance = self._model()
        for query_name, query_value in data.items():

            setattr(instance, self._properties.get(query_name), query_value)

        self._session.add(instance)
        self._session.commit()
        return instance.to_dict()

    def get(self, identifier, query):
        """Fetch a single resource based on some unique identifier.

        Args:
            identifier (str): The string representation of the unique id.
        """
        try:

            model_query = self._session.query(self._model)
            for query_name in self._relevant_values(query):

                model_query = self._filter(
                    model_query,
                    self._properties.get(query_name),
                    query.get(query_name),
                )

            return model_query.filter(
                self._model.primary_key[0] == identifier
            ).one().to_dict()

        except orm_exc.NoResultFound:

            raise exceptions.NotFound()

    def update(self, identifier, data):
        """Update a single resource with new property values.

        Args:
            identifier (str): The string representation of the unique id.
            data (mapping): A mapping of attributes to values which should be
                used when creating the instance.
        """
        data = self._relevant_values(data)

        try:

            instance = self._session.query(self._model).filter(
                self._model.primary_key[0] == identifier
            ).one()

        except orm_exc.NoResultFound:

            raise exceptions.NotFound()

        try:

            for query_name, query_value in data.items():

                setattr(
                    instance,
                    self._properties.get(query_name),
                    query_value,
                )

            self._session.commit()

        except exc.IntegrityError:

            self._session.rollback()
            raise exceptions.BadRequest()

        return instance.to_dict()

    def delete(self, identifier):
        """Delete a single resource with a given identifier.

        Args:
            identifier (str): The string representation of the unique id.
        """
        try:

            instance = self._session.query(self._model).filter(
                self._model.primary_key[0] == identifier
            ).one()
            self._session.delete(instance)
            self._session.commit()

        except orm_exc.NoResultFound:

            pass

        except Exception as err:

            self._session.rollback()
            raise err
