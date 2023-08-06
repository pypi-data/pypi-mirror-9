import re
import json

from flask import request
from json_patch import Patch


from json_patch import PatchError
from json_resource import (
    ResourceNotFound, ValidationError, ResourceExists, UnAuthorized, Forbidden,
    ServiceUnavailable
)
from flask_json_resource.authorization import Authorization
from flask_json_resource import response

EXCEPTION_MAP = {
    ResourceNotFound: 404,
    ResourceExists: 409,
    ValidationError: 422,
    PatchError: 400,
    ValueError: 400,
    UnAuthorized: 401,
    Forbidden: 403,
    ServiceUnavailable: 503
}


class BaseView(object):
    """ Abstract View class. This can be used to create custom views."""
    rel = 'self'
    provide_automatic_options = False

    def __init__(self, resource, authorization=None):
        """ Initialize the view with a resource and an `Authorization` object."""
        self.resource_cls = resource

        if authorization:
            self.authorization = authorization
        else:
            self.authorization = Authorization()

    def resource(self, data, **kwargs):
        return self.resource_cls(data, **kwargs)

    def __call__(self, **kwargs):
        """ Call the view as a function.

        This selects the method based on the request method.

        When an exception occurs, an appropriate error response is created.
        """
        try:
            return getattr(self, request.method.lower())(**kwargs)
        except Exception, e:
            for exception, status_code in EXCEPTION_MAP.items():
                if isinstance(e, exception):
                    return response.ErrorResponse(e, status_code)

            raise

    def options(self, **kwargs):
        return response.OptionsResponse(self.methods, self.resource_cls)

    @property
    def __name__(self):
        """ Returns the name of the view.

        This is used to register the url for this view.
        """
        return '%s-%s' % (self.rel, self.resource_cls.schema['id'].split('.')[0])

    def check_authorization(self):
        """ Checks the authorization of a call.

        This is implemented in the `Authorization object.
        """
        try:
            self.authorization.check_authorization()
        except AttributeError:
            pass

    def authorize(self, resource, **kwargs):
        """ Checks the authorization of a call to access a resource.

        This is implemented in the `Authorization object.
        """
        self.authorization.authorize(resource, **kwargs)

    @property
    def route_options(self):
        """ Options passed when registering
        """
        return {'methods': self.methods}

    @property
    def route(self):
        """ Return a `route` for this object.

        This route is registered in the `flask` app, when the resource is
        registered.

        This use the proper link relation of the schema to determine the path.
        """
        try:
            link = [link for link in self.resource_cls.schema['links']
                    if link['rel'] == self.rel][0]
        except IndexError:
            return

        return re.sub(r'\{(?P<var>[\-\w]+)\}', '<path:\g<var>>', link['href'])


class ResourceView(BaseView):
    """ General view for resources.

    This view will be registered by default in the `API`, and makes it possible
    to retrieve, update and delete resources.
    """
    methods = ['HEAD', 'GET', 'PUT', 'PATCH', 'DELETE', 'OPTIONS']

    def get(self, **kwargs):
        """ Respond to get requests.

        Looks up the resource in the db, and creates a response.

        Returns 200 OK when the resource is found.

        Returns 404 NOT FOUND when the resource does not exist
        """
        self.check_authorization()

        resource = self.resource(kwargs)

        resource.load()
        self.authorize(resource)

        return response.ResourceResponse(resource)

    def put(self, **kwargs):
        """ Respond to PUT requests.

        Replace the resource with the data from the request.

        Returns 200 OK when the resource is found and updated.

        Returns 404 NOT FOUND when the resource does not exist, and it has a
        `create` link specified in the schema

        Returns 400 BAD REQUEST when the request body could not be parsed.

        Return 422 Unprocessable Entity when the request can be parsed, but the
        resource is invalid according to the schema.
        """
        self.check_authorization()

        resource = self.resource(json.loads(request.data))

        if resource.rel('create'):
            upsert = False
        else:
            upsert = True

        self.authorize(resource)

        resource.save(upsert=upsert)

        return response.ResourceResponse(resource)

    def patch(self, **kwargs):
        """ Respond to PATCH requests.

        Returns 200 OK when the resource is found and updated.

        Returns 404 NOT FOUND when the resource does not exist

        Returns 400 BAD REQUEST when the request body could not be parsed, or
        the request body is not a valid json patch.

        Return 422 Unprocessable Entity when the request can be parsed, but the
        resource is invalid according to the schema.
        """
        self.check_authorization()

        resource = self.resource(kwargs)
        resource.load()

        patch = Patch(json.loads(request.data))

        self.authorize(resource)
        resource.patch(patch)
        resource.save()

        return response.ResourceResponse(resource)

    def delete(self, **kwargs):
        """ Respond to DELETE requests.

        Returns 204 OK when the resource is found and deleted.

        Returns 404 NOT FOUND when the resource does not exist
        """
        self.check_authorization()

        resource = self.resource(kwargs).load()
        self.authorize(resource)

        resource.delete()

        return response.DeleteResponse(resource)


class ResourceCreateView(BaseView):
    """ View that allows resources to be created through POST requests.

    This view is registered by default when "create" link is present in the
    schema.
    """
    rel = 'create'
    methods = ['POST', 'OPTIONS']

    def post(self, *args):
        """ Respond to POST requests.

        Returns 201 CREATED when the resource is created.

        Returns 400 BAD REQUEST when the body cannot be parsed

        Returns 422 UNPROCESSABLE ENTITY when the body can be parsed, but the
        resulting resource is not valid according to the schema.


        A `Location` header will be sent with to location of the created user.
        """
        self.check_authorization()

        resource = self.resource(json.loads(request.data))
        self.authorize(resource)

        resource.save(create=True)

        return response.ResourceResponse(resource, status=201)


class SchemaView(ResourceView):
    """ View that is registered for all schemas.

    Only responds to GET requests, since schemas are read-only.
    """
    methods = ['GET', 'OPTIONS']


class CollectionView(ResourceView):
    """ View that is registered for collections.

    Only responds to GET requests.
    """
    methods = ['GET']

    def get(self, **kwargs):
        """ Respond to GET requests.

        Return 200 OK when the list is returned.
        Returns 404 NOT FOUND is a page is requested that does not exist.

        Returns a list of resources. GET parameters can be used to sort and page
        and filter the response.
        """
        self.check_authorization()

        resource = self.resource(kwargs)
        resource['meta'].update(request.args.to_dict())

        self.authorize(resource)

        return response.ResourceResponse(resource.load())
