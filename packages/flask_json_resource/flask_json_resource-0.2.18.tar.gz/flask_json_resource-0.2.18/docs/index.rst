.. include:: ../README.rst

Contents:

.. toctree::
   :maxdepth: 2

Installation
===============

Flask JSON resource can be installed using pip:

    $ pip install flask_json_resource

For development use the -e flag:

    $ pip install -e .


Getting started
===============

First create a `flask` application and and a `flask-pymongo` database:

.. code-block:: python

    from flask import Flask
    from flask.ext import PyMongo
    from flask.ext.json_resource import API

    app = Flask(__name__)
    mongo = PyMongo(app)

Now we can create a `API` object and initialize it with the app and mongo db:

.. code-block:: python

    api = API(app, mongo)

The `api` object exposes two classes that can be used as base classes for the 
resources in your api:

.. code-block:: python

    @api.register()
    class ExampleResource(api.Resource):
        schema = Schema({'id': 'example'})


    @api.register()
    class ExampleCollection(api.Collection):
        schema = Schema({'id': 'example-collection'})

        objects = ExampleResource.objects


The above code registers an `ExampleResource` and a `ExampleCollection` resource 
with the api. It will register views for these resource and expose the resources
using the links described in the schemas of these resources.

The schemas are automatically loaded from the `schemas` dir in your package.


Response Headers
========================

By default the API will return a content-type header and custom link header for
every link defined in the schema:

.. code-block:: http
    GET /examples/test/ HTTP/1.1

    HTTP/1.1 200 OK
    Content-Type: application/json; profile=/schemas/example
    Content-Length: 623
    Connection: keep-alive
    Link: </examples/>; rel=create
    Link: </examples/>; rel=collection
    Link: </schemas/example; rel=describedby

    {'id': 'test'}, ....}

A user-agent should be able to infer the complete api from the links returned.
From this response we can see that the schema of the resource can be found at 
`/schemas/examples`. Likewise, a new resource can be created at `/examples/`

It is possible to control which headers are returned by overwriting the `headers`
property:

.. code-block:: python

    @api.register()
    class ExampleResource(api.Resource):
        schema = Schema({'id': 'example'})

        @property
        def headers(self):
            """ Allow example resources to be stored for up to 600 seconds."""
            headers = super(ExampleResource, self).headers

            headers['Cache-Control'] = 'max-age=600'

            return headers

Authorization
================

Resource can be protected using an Authorization object:

.. code-block:: python

    import requests

    from flask.ext.json_resource import TokenAuthorization, UnAuthorized
    from json_resource import Object
    

    class Token(Object):
        def load(self):
            """ Veirfy the token on the server and load the token data."""
            response = requests.get(
                'http://oauth.example/token',
                headers={
                    'Authorization': 'Bearer %s' % self['access_token'],
                    'Content-type': 'application/json'
                }
            )

            if response.status != 200:
                # Unsuccessfull request. Token must be invalid, so we return 
                # 401 response
                raise UnAuthorized('Invalid Token')
            
            self.update(response.json)
            return self


    class Authorization(TokenAuthorization):
        token_class = Token

        def default(self, resource):
            """ Authorizes the request if the user_id of the token matches
            the user_id of the resource.
            """
            return self.token['user_id'] == self['user_id'] 

        def post(self, resource):
            """ Auhtorize POST request only if `create` is in the scope of this
            token.
            """"
            return 'create' in self.token['scopes']
            

    @api.register(authorization=Authorization):
    class ExampleResource(api.Resource):
        schema = Schema({'id': 'example'})


This protects the ExampleResource, so requests to a resource are only possible
if the user_id of the token matches the user_id of the resource. Resources can
only be created if the token has the `create` scope.


Schemas
=======

Schemas will  be loaded automatically from the `schemas` directory inside your
application. If your application is installed as a package, schemas will also 
be loaded from `<prefix>/var/schemas`.


Views
=====

When registering a resource, it is possible to override wich views will be loaded.


.. code-block:: python

    @api.register(views=[ExampleView])
    class Example(api.Resource):
        schema = Schema({'id': 'test'})


It is also possible to override the views that are registered by setting the
`default_views` attribute:

.. code-block:: python

    class BaseResource(api.Resource):
        default_views = [CustomView, CustomCreationView]


A custom view can be created by extending the BaseView object:

.. code-block:: python

    from flask.ext.json_resource.views import BaseView
    class CustomView(BaseView):
        def get(self, **kwargs):
            # implement custom logic for GET requests here


