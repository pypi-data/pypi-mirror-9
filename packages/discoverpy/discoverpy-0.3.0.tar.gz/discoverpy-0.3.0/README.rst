==========
discoverpy
==========

*REST service framework for discoverable services.*

Writing RESTful services can be repetitive. Every new resource in an API
requires that you pick a URL route, write code to validation data, write a
request handler endpoint, convert your data to something which can be JSON
encoded, JSON encode your data view, add pagination, set all the right headers,
and return the proper response codes. Then you have write a new HTTP client,
create object representation of your REST resources, and handle all your
chosen HTTP response codes. Finally, you get a change to integrate your new
service into the code where you actually wanted it by using your Python client
or hacking it up on the CLI.

This project takes all of that boilerplate work and automates it. You focus
on the important parts of managing your resource data and integrating the
service into your other code. We handle the REST.

Quick Example
=============

.. code-block:: python

    from discoverpy.application import Application
    from discoverpy.service import Service
    from discoverpy.resources.readonly import ReadOnlyResource

    class HelloWorldResource(ReadOnlyResource):

        hellos = [{"name": "world"}, {"name": "hello"}]

        identifier = "name"

        def get(self, query, identifier):
            return {
                "name": identifier,
            }

        def load(self, query):
            return self.hellos

    service = Service(
        name="greeting",
        description="A service for greeting people and machines.",
        version="1",
    )
    service.add(
        HelloWorldResource(
            name="hello",
            description="Greet a person or machine with hello.",

        )
    )

    app = Application(services=[service])

Now run the service under any WSGI server and request away.

.. code-block:: bash

    # Get a paginated list of resources.
    curl "localhost:8888/greeting/v1/hello"
    # Get an instance of a resource.
    curl "localhost:8888/greeting/v1/hello/you"

    # See your new service in the API discovery service.
    curl "localhost:8888/discover/v1/service?name=greeting"
    curl "localhost:8888/discover/v1/resource?service=greeting&version=1"

The example is degenerate, but the principle should visible: You don't have to
deal with boilerplate. Implementing a resource class which can manage your data
is sufficient and the framework will handle the HTTP bits.

Service Discovery API
=====================

The namesake of the project is rooted in the automatic service discovery API
which is generated with each WSGI application. It uses the metadata given
when you create Service or Resource objects to construct an API which allows
consumers to see what services your endpoint provides, what resources are
exposed by those services, and the JSON schema used to validate input.

The service discovery API works as follows:

-   GET /discover/v1/service

    Get a paginated list of all services registered with the WSGI application.

-   GET /discover/v1/service/{service name}?version={service version}

    Get an instance of a service.

-   GET /discover/v1/resource?service={service name}&version={service version}

    Get a paginated list of resources registered with the service.

-   GET /discover/v1/resource/{resource name}?service={service name}&version={service version}

    Get an instance of a resource.

This API is used to power the automatic client.

Automatic Client
================

The project ships with a Python client which leverages the service discovery
API to automatically provide an interface to new services and resources.

.. code-block:: python

    from discoverpy.client.api import Client

    client = Client(endpoint='http://localhost:8888')

    # Iterate over all services and resources.
    for service in client.services:

        print('name: {0}, version: {1}, description: {2}'.format(
            service.name,
            service.version,
            service.description,
        ))

        for resource in service.resources:

            print('name: {0}, description: {1}'.format(
                resource.name,
                resource.description,
            ))

    # Get a specific resource and iterate over its paginated output.
    resource = client.service('greeting', version='1').resource('hello')
    for hello in resource.load():

        print('name: {0}'.format(hello.name))

Resource Classes
================

There is a base Resource class which can be extended, but resources can be any
Python object which expose the following signatures:

    -   identifier

        The field name of the resource identifier in a payload.

    -   name

        The name of the resource.

    -   description

        The description of the resource.

    -   validator

        The JSON schema validator to use with the resource.

    -   load(query)

        Return a two-tuple where the first element is the paginated content
        and the second is the total number of items which match the query.

    -   get(query, identifier)

        Return a single resource matching the query.

    -   create(query, data)

        Create a new resource and return it.

    -   update(query, identifier, data)

        Update an instance and return the new data.

    -   delete(query, identifier)

        Delete the given resource

The get, load, create, update, and delete methods should return Python
dictionaries which can be JSON encoded. In each method the query parameter will
be a special Query object which wraps a URL query string for easier management,
the identifier will the the last portion of a URL, and data will be a Python
dictionary which was decoded from JSON input.

Any complete implementation of the Resource interface may be passed to the
Service object. There are built in versions of Resource which provide some
handy features.

The resources.readonly.ReadOnlyResource allows subclasses to only implement
get and load. It will handle the other methods appropriately. The
resources.sqlalchemy.SqlalchemyResource allows you to pass in a SQLAlchemy ORM
model and generate an API around it. Look at the SqlalchemyResource as an
example for how complex resources may be implemented.

License
=======

::

    (MIT License)

    Copyright (C) 2015 Kevin Conway

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to
    deal in the Software without restriction, including without limitation the
    rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
    sell copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
    IN THE SOFTWARE.


Contributing
============

All contributions to this project are protected under the agreement found in
the `CONTRIBUTING` file. All contributors should read the agreement but, as
a summary::

    You give us the rights to maintain and distribute your code and we promise
    to maintain an open source distribution of anything you contribute.
