#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
HTTP request objects.  Ported from webapp2, refactored to
support Python versions > 2.7, 3.0
"""

import sys
import cgi
import webob

if sys.version < '3':
    # python 2.7 compatibility
    from urllib import urlencode
    from cStringIO import StringIO

else:
    # python 3.0 compatibility
    from urllib.parse import urlencode
    from io import BytesIO as StringIO

from .utils.strings import _basestring, _bytes

#<----------------------------------------------------------------------------->

class Request(webob.Request):
    """Abstraction for an HTTP request.

    Most extra methods and attributes are ported from webapp. Check the
    `WebOb documentation <WebOb>`_ for the ones not listed here.
    """

    #: A reference to the active :class:`WSGIApplication` instance.
    app = None
    
    #: A reference to the active :class:`Response` instance.
    response = None
    
    #: A reference to the matched :class:`Route`.
    route = None
    
    #: The matched route positional arguments.
    route_args = None
    
    #: The matched route keyword arguments.
    route_kwargs = None
    
    #: A dictionary to register objects used during the request lifetime.
    registry = None
    
    # Attributes from webapp.
    request_body_tempfile_limit = 0
    uri = property(lambda self: self.url)
    query = property(lambda self: self.query_string)

    def __init__(self, environ, *args, **kwargs):
        """Constructs a Request object from a WSGI environment.

        :param environ:
            A WSGI-compliant environment dictionary.
        """
        unicode_errors = kwargs.pop('unicode_errors', 'ignore')
        decode_param_names = kwargs.pop('decode_param_names', True)
        super(Request, self).__init__(environ, unicode_errors=unicode_errors,
                                      decode_param_names=decode_param_names,
                                      *args, **kwargs)
        self.registry = {}

    def get(self, argument_name, default_value=''):
        """Returns the query or POST argument with the given name.

        We parse the query string and POST payload lazily, so this will be a
        slower operation on the first call.

        :param argument_name:
            The name of the GET, POST, PUT or DELETE argument.
        :param default_value:
            The value to return if the given argument is not present.
        :returns:
            Returns the first value with the given name given in the request.
            Use the get_all method to return a list of all values with the 
            specified argument name.
        """
        param_value = self.get_all(argument_name)

        if len(param_value) > 0:
            return param_value[0]
        
        else:
            return default_value

    def get_all(self, argument_name, default_value=None):
        """Returns a list of query or POST arguments with the given name.

        We parse the query string and POST payload lazily, so this will be a
        slower operation on the first call.

        :param argument_name:
            The name of the query or POST argument.
        :param default_value:
            The value to return if the given argument is not present,
            None may not be used as a default, if it is then an empty
            list will be returned instead.
        :returns:
            A (possibly empty) list of values.
        """

        if default_value is None:
            default_value = []

        param_value = self.params.getall(argument_name)

        if param_value is None or len(param_value) == 0:
            return default_value

        for i in range(len(param_value)):
            if isinstance(param_value[i], cgi.FieldStorage):
                param_value[i] = param_value[i].value

        return param_value

    def arguments(self):
        """Returns a list of the arguments provided in the query and/or POST.

        The return value is a list of strings.
        """
        return list(set(self.params.keys()))

    def get_range(self, name, min_value=None, max_value=None, default=0):
        """Parses the given int argument, limiting it to the given range.

        :param name:
            The name of the argument.
        :param min_value:
            The minimum int value of the argument (if any).
        :param max_value:
            The maximum int value of the argument (if any).
        :param default:
            The default value of the argument if it is not given.
        :returns:
            An int within the given range for the argument.
        """
        value = self.get(name, default)
        if value is None:
            return value

        try:
            value = int(value)
        except ValueError:
            value = default
            if value is not None:
                if max_value is not None:
                    value = min(value, max_value)

                if min_value is not None:
                    value = max(value, min_value)

        return value

    @classmethod
    def blank(cls, path, environ=None, base_url=None, headers=None, **kwargs): # pragma: no cover
        """Adds parameters compatible with WebOb >= 1.0: POST and **kwargs."""
        
        try:
            return super(Request, cls).blank(path, environ=environ,
                base_url=base_url, headers=headers, **kwargs)
        except TypeError:
            if not kwargs:
                raise

        data = kwargs.pop('POST', None)
        
        if data is not None:
            environ = environ or {}
            environ['REQUEST_METHOD'] = 'POST'
            
            if hasattr(data, 'items'):
                data = data.items()
            
            if not isinstance(data, _bytes):
                data = urlencode(data)
            
            environ['wsgi.input'] = StringIO(data.encode('utf-8'))
            environ['webob.is_body_seekable'] = True
            environ['CONTENT_LENGTH'] = str(len(data))
            environ['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'

        base = super(Request, cls).blank(path, environ=environ,
                    base_url=base_url, headers=headers)
        if kwargs:
            obj = cls(base.environ, **kwargs)
            obj.headers.update(base.headers)
            return obj
        else:
            return base

#<----------------------------------------------------------------------------->

class RequestContext(object):
    """Context for a single request.

    The context is responsible for setting and cleaning global variables for
    a request.
    """

    #: A :class:`WSGIApplication` instance.
    app = None
    #: WSGI environment dictionary.
    environ = None

    def __init__(self, app, environ):
        """Initializes the request context.

        :param app:
            An :class:`WSGIApplication` instance.
        :param environ:
            A WSGI environment dictionary.
        """
        self.app = app
        self.environ = environ

    def __enter__(self):
        """Enters the request context.

        :returns:
            A tuple ``(request, response)``.
        """
        
        # Build request and response.
        request = self.app.request_class(self.environ)
        response = self.app.response_class()
        
        # Make active app and response available through the request object.
        request.app = self.app
        request.response = response
        
        # Register global variables.
        self.app.set_globals(app=self.app, request=request)
        return request, response

    def __exit__(self, exc_type, exc_value, traceback):
        """Exits the request context.

        This release the context locals except if an exception is caught
        in debug mode. In this case they are kept to be inspected.
        """
        if exc_type is None or not self.app.debug:
            # Unregister global variables.
            self.app.clear_globals()
