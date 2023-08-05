#!/usr/bin/python
# -*- coding: utf-8 -*-

from webob import exc
from .utils.http import abort
from .wsgi import WSGIApplication
from .helpers import redirect, get_app

#<----------------------------------------------------------------------------->

def _normalize_handler_method(method):
    """Transforms an HTTP method into a valid Python identifier."""
    return method.lower().replace('-', '_')

#<----------------------------------------------------------------------------->

def _get_handler_methods(handler):
    """Returns a list of HTTP methods supported by a handler.

    :param handler:
        A :class:`RequestHandler` instance.
    :returns:
        A list of HTTP methods supported by the handler.
    """
    methods = []
    for method in get_app().allowed_methods:
        if getattr(handler, _normalize_handler_method(method), None):
            methods.append(method)

    return methods

#<----------------------------------------------------------------------------->

class RequestHandler(object):
    """Base HTTP request handler."""

    #: A :class:`webtools.request.Request` instance.
    request = None
    
    #: A :class:`webtools.response.Response` instance.
    response = None
    
    #: A :class:`webtools.wsgi.WSGIApplication` instance.
    app = None

    #<------------------------------------------------------------------------->

    authorize = None
    """Validates if a request has been authenticated. Authorize should be set to 
    a callable that accepts one parameter, a :class:`webtools.handlers.RequestHandler` 
    subclass instance. The callable should return True if the request is allowed 
    to proceed and False otherwise. If False, a 401 Not Authorized error will be 
    raised::

        def my_authorizer(handler):
            # Maybe do something with the request object attached to the handler
            if request_is_authorized:
                return True
            else:
                return False

        class MyHandler(RequestHandler):
            authorize = my_authorizer

            def get(self):
                self.response.write('Only authorized requests can see this')
    """

    authorize_methods = []
    """Lists the HTTP methods that :meth:`authorize` should validate. By default, 
    :meth:`authorize` validates all methods. If set, :meth:`authorize` will 
    validate only those HTTP methods specified and ignore any others::

        class MyHandler(RequestHandler):
            authorize = my_authorizer
            authorize_methods = ['post']

            def get(self):
                self.response.write('Anyone can see a GET request')

            def post(self):
                self.response.write('Only those authorized can POST')
    """

    #<------------------------------------------------------------------------->
    
    cache_control = ''
    """Sets the HTTP Cache-Control header in the response for GET requests. Defaults
    to the value specified by `default_cache_control` if blank. Care should be 
    taken when setting this attribute."""

    default_cache_control = 'max-age=0, no-cache, no-store'
    """Sets the default value for the HTTP Cache-Control header in the response.
    This applies to all HTTP request methods (i.e. GET, POST, etc..). This
    attibute should not be modified in most use casses.
    """

    #<------------------------------------------------------------------------->

    def __init__(self, request=None, response=None):
        """Initializes this request handler with the given WSGI application,
        Request and Response.

        When instantiated by ``webtools.WSGIApplication``, request and response
        are not set on instantiation. Instead, initialize() is called right
        after the handler is created to set them.

        Dispatching is handle by webtools to allow more flexibility in extended 
        classes: handlers can wrap :meth:`dispatch` to check for conditions 
        before executing the requested method and/or post-process the response.

        .. note::
           Parameters are optional only to support webtools constructor which
           doesn't take any arguments. Consider them as required.

        :param request:
            A :class:`Request` instance.
        :param response:
            A :class:`Response` instance.
        """
        self.initialize(request, response)

    def initialize(self, request, response):
        """Initializes this request handler with the given WSGI application,
        Request and Response.

        :param request:
            A :class:`Request` instance.
        :param response:
            A :class:`Response` instance.
        """
        self.app = WSGIApplication.active_instance
        self.response = response
        self.request = request

        # normalize the authorize methods
        if self.authorize_methods:
            try:
                self.authorize_methods = [_normalize_handler_method(method) 
                    for method in self.authorize_methods]
            except TypeError:
                raise Exception("""authorize_methods must be set to a list 
                    or tuple of method names (i.e. ['get', 'post']""")
        
    def _authorize(self, method_name):
        """Authorizes the request

        This method is called prior to dispatching the request to the appropriate
        HTTP handler method (i.e. get(), post(), etc..). The _authorize method
        calls self.authorize (if set) and raises a 401 Not Authorized error if 
        self.authorize returns False.  By default, authorize will test all
        HTTP methods.  If self.authorize_methods is set, authorize will
        only test the methods specified.
        """

        if self.authorize:
            if not self.authorize_methods or method_name in self.authorize_methods:
                if not self.authorize():
                    self.abort(401) # 401 Not Authorized

    def dispatch(self):
        """Dispatches the request.

        This will first check if there's a handler_method defined in the
        matched route, and if not it'll use the method correspondent to the
        request method (``get()``, ``post()`` etc).
        """
        request = self.request
        method_name = request.route.handler_method
        if not method_name:
            method_name = _normalize_handler_method(request.method)

        method = getattr(self, method_name, None)
        if method is None:
            # 405 Method Not Allowed.
            # The response MUST include an Allow header containing a
            # list of valid methods for the requested resource.
            # http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html#sec10.4.6
            valid = ', '.join(_get_handler_methods(self))
            self.abort(405, headers=[('Allow', valid)])

        # Authorize the request
        self._authorize(method_name)

        # Set the HTTP Cache-Control header for the response
        self.response.cache_control = self.default_cache_control
        if method_name == 'get' and self.cache_control:
            self.response.cache_control = self.cache_control

        # The handler only receives *args if no named variables are set.
        args, kwargs = request.route_args, request.route_kwargs
        if kwargs:
            args = ()

        try:
            return method(*args, **kwargs)
        except Exception as e:
            return self.handle_exception(e, self.app.debug)

    def error(self, code):
        """Clears the response and sets the given HTTP status code.

        This doesn't stop code execution; for this, use :meth:`abort`.

        :param code:
            HTTP status error code (e.g., 501).
        """
        self.response.status = code
        self.response.clear()

    def abort(self, code, *args, **kwargs):
        """Raises an :class:`HTTPException`.

        This stops code execution, leaving the HTTP exception to be handled
        by an exception handler.

        :param code:
            HTTP status code (e.g., 404).
        :param args:
            Positional arguments to be passed to the exception class.
        :param kwargs:
            Keyword arguments to be passed to the exception class.
        """
        abort(code, *args, **kwargs)

    def redirect(self, uri, permanent=False, abort=False, code=None, body=None):
        """Issues an HTTP redirect to the given relative URI.

        The arguments are described in :func:`redirect`.
        """
        return redirect(uri, permanent=permanent, abort=abort, code=code,
                        body=body, request=self.request,
                        response=self.response)

    def redirect_to(self, _name, _permanent=False, _abort=False, _code=None,
                    _body=None, *args, **kwargs):
        """Convenience method mixing :meth:`redirect` and :meth:`uri_for`.

        The arguments are described in :func:`redirect` and :func:`uri_for`.
        """
        uri = self.uri_for(_name, *args, **kwargs)
        return self.redirect(uri, permanent=_permanent, abort=_abort,
                             code=_code, body=_body)

    def uri_for(self, _name, *args, **kwargs):
        """Returns a URI for a named :class:`Route`.

        .. seealso:: :meth:`webtools.route.Router.build`.
        """
        return self.app.router.build(self.request, _name, args, kwargs)
    

    def handle_exception(self, exception, debug):
        """Called if this handler throws an exception during execution.

        The default behavior is to re-raise the exception to be handled by
        :meth:`WSGIApplication.handle_exception`.

        :param exception:
            The exception that was thrown.
        :param debug_mode:
            True if the web application is running in debug mode.
        """
        raise

#<----------------------------------------------------------------------------->

class RedirectHandler(RequestHandler):
    """Redirects to the given URI for all GET requests.

    This is intended to be used when defining URI routes. You must provide at
    least the keyword argument *url* in the route default values. Example::

        def get_redirect_url(handler, *args, **kwargs):
            return handler.uri_for('new-route-name')

        app = WSGIApplication([
            Route('/old-url', RedirectHandler, defaults={'_uri': '/new-url'}),
            Route('/other-old-url', RedirectHandler, defaults={'_uri': get_redirect_url}),
        ])
    """

    def get(self, *args, **kwargs):
        """Performs a redirect.

        Two keyword arguments can be passed through the URI route:

        - **_uri**: A URI string or a callable that returns a URI. The callable
          is called passing ``(handler, *args, **kwargs)`` as arguments.
        - **_code**: The redirect status code. Default is 301 (permanent
          redirect).
        """
        uri = kwargs.pop('_uri', '/')
        permanent = kwargs.pop('_permanent', True)
        code = kwargs.pop('_code', None)

        func = getattr(uri, '__call__', None)
        if func:
            uri = func(self, *args, **kwargs)

        self.redirect(uri, permanent=permanent, code=code)