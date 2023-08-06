"""
    Implements the server side operations on models and instances.
"""
from urllib import quote, urlencode

from django.core.urlresolvers import reverse
from django.db.models import Model

from slumber.server import get_slumber_root


def _forbidden(_request, response, *_):
    """Return an error to say that the method type is not allowed.
    """
    response['_meta']['status'] = 405
    response['_meta']['message'] = "Method Not Allowed"


class Operation(object):
    """Base class for operations. The ModelOperation and InstanceOperation
    classes are for backward compatibility, but their use is deprecated.
    """
    METHODS = ['GET', 'OPTIONS', 'POST', 'PUT', 'DELETE']

    def __init__(self, model, name, uri=None):
        self.model = model
        self.name = name
        self.uri = uri
        self.regex = ''
        self.path = model.path + name + '/'

    def __call__(self, *args, **qs):
        root = get_slumber_root()
        uri = self.uri or (root + self.path)
        for part in args:
            if issubclass(type(part), Model):
                part = part.pk
            part = str(part)
            if part.startswith('/'):
                if part.startswith(root):
                    uri = part
                else:
                    uri = root + part[1:]
            else:
                uri += quote(part)
            if not uri.endswith('/'):
                uri += '/'
        if qs:
            uri += '?' + urlencode(qs)
        return uri

    def headers(self, retvalue, request, response):
        """Calculate and place extra headers needed for certain types of
        response.
        """
        if response['_meta']['status'] == 405 or request.method == 'OPTIONS':
            response['_meta'].setdefault('headers', {})
            response['_meta']['headers']['Allow'] = \
                ', '.join([method
                    for method in self.METHODS
                        if hasattr(self, method.lower())])
        return retvalue

    def operation(self, request, response, _appname, _model, *args):
        """Perform the requested operation in the server.
        """
        if request.method in self.METHODS:
            retvalue = getattr(self, request.method.lower(), _forbidden)(
                request, response, *args)
            return self.headers(retvalue, request, response)
        else:
            _forbidden(request, response)
        return self.headers(None, request, response)

    def options(self, request, response, *_):
        """A standard options response that will fill in the Allow header.
        """
        return self.headers(None, request, response)


class ModelOperation(Operation):
    """Base class for model operations.
    """
    model_operation = True

    def operation(self, request, response, *args):
        """Perform the requested operation in the server.
        """
        if request.method in self.METHODS:
            retvalue = getattr(self, request.method.lower(), _forbidden)(
                request, response, *args)
            return self.headers(retvalue, request, response)
        else:
            _forbidden(request, response)
        return self.headers(None, request, response)


class InstanceOperation(ModelOperation):
    """Base class for operations on instances.
    """
    model_operation = False
    def __init__(self, model, name, uri=None):
        super(InstanceOperation, self).__init__(model, name, uri)
        self.regex = '([^/]+)/'

