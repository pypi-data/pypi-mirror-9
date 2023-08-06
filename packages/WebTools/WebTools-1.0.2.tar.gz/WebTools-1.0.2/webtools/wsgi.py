#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from wsgiref.handlers import CGIHandler
from webob import exc
from .request import Request, RequestContext
from .response import Response
from .route import Router
from .utils.strings import _basestring, import_string

#<----------------------------------------------------------------------------->

# Make WSGI application thread safe
_local = None

try: # pragma: no cover
    # Thread-local variables container.
    from .utils import local
    _local = local.Local()

except ImportError: # pragma: no cover
    logging.warning("WebTools is unable to import the local module from utils, \
    	application will not be thread safe!")

#<----------------------------------------------------------------------------->

ALLOWED_METHODS = frozenset(
	('GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'DELETE', 'TRACE')
)

#<----------------------------------------------------------------------------->

class WSGIConfig(dict):
    """A simple configuration dictionary for the :class:`WSGIApplication`.

    Can be used to load configuration settings for application sub modules::

        config = {'app.submodule': {'key', 'value'}}

        app = WSGIApplication([], config=config)

        submodule_config = app.config.load_config('app.submodule')
    """

    #: Loaded configurations.
    loaded = None

    def __init__(self, defaults=None):
        dict.__init__(self, defaults or ())
        self.loaded = []

    def load_config(self, key, default_values=None, user_values=None,
                    required_keys=None):
        """Returns a configuration for a given key.

        This can be used by objects that define a default configuration. It
        will update the app configuration with the default values the first
        time it is requested, and mark the key as loaded.

        :param key:
            A configuration key.
        :param default_values:
            Default values defined by a module or class.
        :param user_values:
            User values, used when an object can be initialized with
            configuration. This overrides the app configuration.
        :param required_keys:
            Keys that can not be None.
        :raises:
            Exception, when a required key is not set or is None.
        """
        if key in self.loaded:
            config = self[key]
        else:
            config = dict(default_values or ())
            if key in self:
                config.update(self[key])

            self[key] = config
            self.loaded.append(key)
            if required_keys and not user_values:
                self._validate_required(key, config, required_keys)

        if user_values:
            config = config.copy()
            config.update(user_values)
            if required_keys:
                self._validate_required(key, config, required_keys)

        return config

    def _validate_required(self, key, config, required_keys):
        missing = [k for k in required_keys if config.get(k) is None]

        if missing:
            error_msg = 'Missing configuration keys for {!r}: {!r}.'
            raise Exception(error_msg.format(key, missing))

#<----------------------------------------------------------------------------->

class WSGIApplication(object):
    """A WSGI-compliant application."""

    #: Allowed request methods.
    allowed_methods = ALLOWED_METHODS
    
    #: Class used for the request object.
    request_class = Request
    
    #: Class used for the response object.
    response_class = Response
    
    #: Class used for the router object.
    router_class = Router
    
    #: Class used for the request context object.
    request_context_class = RequestContext
    
    #: Class used for the configuration object.
    config_class = WSGIConfig
    
    #: A general purpose flag to indicate development mode: if True, uncaught
    #: exceptions are raised instead of using ``HTTPInternalServerError``.
    debug = False
    
    #: A :class:`Router` instance with all URIs registered for the application.
    router = None
    
    #: A :class:`Config` instance with the application configuration.
    config = None
    
    #: A dictionary to register objects used during the app lifetime.
    registry = None
    
    #: A dictionary mapping HTTP error codes to callables to handle those
    #: HTTP exceptions. See :meth:`handle_exception`.
    error_handlers = None
    
    #: Active :class:`WSGIApplication` instance. See :meth:`set_globals`.
    app = None
    
    #: Active :class:`Request` instance. See :meth:`set_globals`.
    request = None
    
    #: Same as :attr:`app`, for webapp compatibility. See :meth:`set_globals`.
    active_instance = None

    def __init__(self, routes=None, debug=False, config=None):
        """Initializes the WSGI application.

        :param routes:
            A sequence of :class:`Route` instances or, for simple routes,
            tuples ``(regex, handler)``.
        :param debug:
            True to enable debug mode, False otherwise.
        :param config:
            A configuration dictionary for the application.
        """
        self.debug = debug
        self.registry = {}
        self.error_handlers = {}
        self.set_globals(app=self)
        self.config = self.config_class(config)
        self.router = self.router_class(routes)

    def set_globals(self, app=None, request=None):
        """Registers the global variables for app and request.

        If :mod:`webbox.utils.local` is available the app and request
        class attributes are assigned to a proxy object that returns them
        using thread-local, making the application thread-safe. This can also
        be used in environments that don't support threading.

        If :mod:`webbox.utils.local` is not available app and request will
        be assigned directly as class attributes. This should only be used in
        non-threaded environments.

        :param app:
            A :class:`WSGIApplication` instance.
        :param request:
            A :class:`Request` instance.
        """
        if _local is not None: # pragma: no cover
            _local.app = app
            _local.request = request
        else: # pragma: no cover
            WSGIApplication.app = WSGIApplication.active_instance = app
            WSGIApplication.request = request

    def clear_globals(self):
        """Clears global variables. See :meth:`set_globals`."""
        if _local is not None: # pragma: no cover
            _local.__release_local__()
        else: # pragma: no cover
            WSGIApplication.app = WSGIApplication.active_instance = None
            WSGIApplication.request = None

    def __call__(self, environ, start_response):
        """Called by WSGI when a request comes in.

        :param environ:
            A WSGI environment.
        :param start_response:
            A callable accepting a status code, a list of headers and an
            optional exception context to start the response.
        :returns:
            An iterable with the response to return to the client.
        """
        with self.request_context_class(self, environ) as (request, response):
            try:
                if request.method not in self.allowed_methods:
                    # 501 Not Implemented.
                    raise exc.HTTPNotImplemented()

                rv = self.router.dispatch(request, response)
                if rv is not None:
                    response = rv
            except Exception as e:
                try:
                    # Try to handle it with a custom error handler.
                    rv = self.handle_exception(request, response, e)
                    if rv is not None:
                        response = rv
                except exc.HTTPException as e:
                    # Use the HTTP exception as response.
                    response = e
                except Exception as e:
                    # Error wasn't handled so we have nothing else to do.
                    response = self._internal_error(e)

            try:
                return response(environ, start_response)
            except Exception as e:
                return self._internal_error(e)(environ, start_response)

    def _internal_error(self, exception):
        """Last resource error for :meth:`__call__`."""
        logging.exception(exception)
        if self.debug:
            raise

        return exc.HTTPInternalServerError()

    def handle_exception(self, request, response, e):
        """Handles a uncaught exception occurred in :meth:`__call__`.

        Uncaught exceptions can be handled by error handlers registered in
        :attr:`error_handlers`. This is a dictionary that maps HTTP status
        codes to callables that will handle the corresponding error code.
        If the exception is not an ``HTTPException``, the status code 500
        is used.

        The error handlers receive (request, response, exception) and can be
        a callable or a string in dotted notation to be lazily imported.

        If no error handler is found, the exception is re-raised.

        Based on idea from Flask.

        :param request:
            A :class:`Request` instance.
        :param request:
            A :class:`Response` instance.
        :param e:
            The uncaught exception.
        :returns:
            The returned value from the error handler.
        """
        if isinstance(e, exc.HTTPException):
            code = e.code
        else:
            code = 500

        handler = self.error_handlers.get(code)
        if handler:
            if isinstance(handler, _basestring):
                self.error_handlers[code] = handler = import_string(handler)

            return handler(request, response, e)
        else:
            # Re-raise it to be caught by the WSGI app.
            raise

    def run(self):
        """
        Runs this WSGI-compliant application in a CGI environment.
        Uses ``wsgiref.handlers.CGIHandler().run()``.
        """
        CGIHandler().run(self.app)

    def get_response(self, *args, **kwargs):
        """Creates a request and returns a response for this app.

        This is a convenience for unit testing purposes. It receives
        parameters to build a request and calls the application, returning
        the resulting response::

            class HelloHandler(webapp2.RequestHandler):
                def get(self):
                    self.response.write('Hello, world!')

            app = webapp2.WSGIapplication([('/', HelloHandler)])

            # Test the app, passing parameters to build a request.
            response = app.get_response('/')
            assert response.status_int == 200
            assert response.body == 'Hello, world!'

        :param args:
            Positional arguments to be passed to ``Request.blank()``.
        :param kwargs:
            Keyword arguments to be passed to ``Request.blank()``.
        :returns:
            A :class:`Response` object.
        """
        return self.request_class.blank(*args, **kwargs).get_response(self)

#<----------------------------------------------------------------------------->

def _set_thread_safe_app():
    """Assigns WSGIApplication globals to a proxy pointing to thread-local."""
    if _local is not None: # pragma: no cover
        WSGIApplication.app = WSGIApplication.active_instance = _local('app')
        WSGIApplication.request = _local('request')

#<----------------------------------------------------------------------------->

# Set Request and Response classes
Request.ResponseClass = Response
Response.RequestClass = Request

# Thread-safety support.
_set_thread_safe_app()
