import re

from json_resource import ResourceNotFound, Forbidden, UnAuthorized
from flask import request, g


class Authorization(object):
    """ Authorization base object.

    Extend this to implement custom authorization in your API.
    """

    def check_authorization(self):
        """ Perform authorization on the request, and raise an UnAuthorized
        exception when not authorized.

        Check that the request meets basic requirements for authorization
        (e.g., such as proper authorization headers). This is called in
        situations where authorization must be performed before a resource
        is checked.
        """
        pass

    def authorize(self, resource, **kwargs):
        """ Authorize `resource` against the request.

        Check if a method that corresponds to the request method exists on
        the object.

        If this method returns `True` the request is authorized. if the method
        returns `False`, the request is not allowed and a Forbidden error
        is raised.

        If no method corresponding to the request method exists, the `default`
        method is called.
        """
        method = request.method.lower()

        if hasattr(self, method):
            func = getattr(self, method)
        else:
            func = self.default

        if not func(resource, **kwargs):
            raise Forbidden('Access Denied')

    def default(self, resource):
        """ Default authorization method.

        This is called if no method corresponding to the request method exists.
        """
        return True


class TokenAuthorization(Authorization):
    """ Token Authorization base object.

    Extend this to implement token based authorization
    """
    token_class = None

    @property
    def token_string(self):
        header = request.headers.get('Authorization')

        try:
            return re.match(
                r'^Bearer (?P<token>.+)$', header
            ).group('token')
        except TypeError:
            raise UnAuthorized('Missing authorization header')
        except AttributeError:
            raise UnAuthorized('Invalid authorization header')

    @property
    def token(self):
        """ Return the current token.

        Raises an Unauthorized error if no bearer token is supplied in the
        request.
        """
        # Cache token retrieval in request context
        if '_flask_json_resource_token' in g:
            return g._flask_json_resource_token

        try:
            g._flask_json_resource_token = \
                self.token_class({'access_token': self.token_string}).load()
            return g._flask_json_resource_token
        except (ResourceNotFound, UnAuthorized):
            raise UnAuthorized('Invalid Access token')

    def check_authorization(self):
        """ Trigger token authorization.

        Raises an Unauthorized error if no bearer token is supplied in the
        request, or if the underlying token object can not be created.
        """
        self.token
