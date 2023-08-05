import hashlib
import json

import json_resource

from . import views


class Schema(json_resource.Schema):
    """ Schema resource.

    Extends `json_resource.schema` to add some functionality for exposing
    schemas through the api
    """
    default_views = [views.SchemaView]
    meta = {}

    @property
    def etag(self):
        """ Return the etag of the resource."""
        return hashlib.md5(json.dumps(self)).hexdigest()

