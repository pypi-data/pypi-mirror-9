#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
URI building and routing classes.  Ported from webapp2, refactored to
support Python versions > 2.7, 3.0
"""

import inspect
import sys
import re

if sys.version < '3':
    # python 2.7 compatibility
    from urllib import urlencode
    from urlparse import urlunsplit
    from urllib import quote as urlquote
    from urllib import unquote as urlunquote

else:
    # python 3.0 compatibility
    from urllib.parse import urlencode, urlunsplit
    from urllib.parse import quote as urlquote
    from urllib.parse import unquote as urlunquote


from webob import exc
from .adapters import BaseHandlerAdapter, WebToolsHandlerAdapter
from .utils.decorators import cached_property
from .utils.strings import import_string, _basestring, _to_utf8

#<----------------------------------------------------------------------------->

#: Regex for route definitions.
_route_re = re.compile(r"""
    \<               # The exact character "<"
    ([a-zA-Z_]\w*)?  # The optional variable name
    (?:\:([^\>]*))?  # The optional :regex part
    \>               # The exact character ">"
    """, re.VERBOSE)

#<----------------------------------------------------------------------------->

def _parse_route_template(uri_template, default_sufix=''):
    """Lazy route template parser."""
    variables = {}
    reverse_uri_template = pattern = ''
    args_count = last = 0
    for match in _route_re.finditer(uri_template):
        part = uri_template[last:match.start()]
        name = match.group(1)
        expr = match.group(2) or default_sufix
        last = match.end()

        if not name:
            name = '__{:d}__'.format(args_count)
            args_count += 1

        pattern += '{}(?P<{}>{})'.format(re.escape(part), name, expr)
        reverse_uri_template += '{}%({})s'.format(part, name)
        variables[name] = re.compile('^{}$'.format(expr))

    part = uri_template[last:]
    kwargs_count = len(variables) - args_count
    reverse_uri_template += part
    regex = re.compile('^{}{}$'.format(pattern, re.escape(part)))
    return regex, reverse_uri_template, args_count, kwargs_count, variables

#<----------------------------------------------------------------------------->

def _urlunsplit(scheme=None, netloc=None, path=None, query=None, fragment=None):
    """Like ``urlparse.urlunsplit``, but will escape values and urlencode and
    sort query arguments.

    :param scheme:
        URI scheme, e.g., `http` or `https`.
    :param netloc:
        Network location, e.g., `localhost:8080` or `www.google.com`.
    :param path:
        URI path.
    :param query:
        URI query as an escaped string, or a dictionary or list of key-values
        tuples to build a query.
    :param fragment:
        Fragment identifier, also known as "anchor".
    :returns:
        An assembled absolute or relative URI.
    """
    if not scheme or not netloc:
        scheme = ''
        netloc = ''

    if path:
        path = urlquote(_to_utf8(path))

    if query and not isinstance(query, _basestring):
        if isinstance(query, dict):
            query = iter(query.items())

        # Sort args: commonly needed to build signatures for services.
        query = urlencode(sorted(query))

    if fragment:
        fragment = urlquote(_to_utf8(fragment))

    return urlunsplit((scheme, netloc, path, query, fragment))

#<----------------------------------------------------------------------------->

def _get_route_variables(match, default_kwargs=None):
    """Returns (args, kwargs) for a route match."""
    kwargs = default_kwargs or {}
    kwargs.update(match.groupdict())
    if kwargs:
        keys = tuple(key for key in kwargs.keys() if key.startswith('__') and key.endswith('__'))
        values = sorted((int(key[2:-2]), kwargs.pop(key)) for key in keys)
        args = tuple(value[1] for value in values)

    else:
        args = ()

    return args, kwargs

#<----------------------------------------------------------------------------->

class BaseRoute(object):
    """Interface for URI routes."""

    #: The uri regex template.
    uri_template = None
    
    #: Route name, used to build URIs.
    name = None
    
    #: True if this route is only used for URI generation and never matches.
    build_only = False
    
    #: The handler or string in dotted notation to be lazily imported.
    handler = None
    
    #: The custom handler method, if handler is a class.
    handler_method = None
    
    #: The handler, imported and ready for dispatching.
    handler_adapter = None

    def __init__(self, uri_template, handler=None, name=None, build_only=False):
        """Initializes this route.

        :param uri_template:
            A regex to be matched.
        :param handler:
            A callable or string in dotted notation to be lazily imported,
            e.g., ``'my.module.MyHandler'`` or ``'my.module.my_function'``.
        :param name:
            The name of this route, used to build URIs based on it.
        :param build_only:
            If True, this route never matches and is used only to build URIs.
        """
        if build_only and name is None:
            error_msg = "Route {!r} is build_only but doesn't have a name.".format(self)
            raise ValueError(error_msg)

        self.uri_template = uri_template
        self.handler = handler
        self.name = name
        self.build_only = build_only

    def match(self, request):
        """Matches all routes against a request object.

        The first one that matches is returned.

        :param request:
            A :class:`Request` instance.
        :returns:
            A tuple ``(route, args, kwargs)`` if a route matched, or None.
        """
        raise NotImplementedError()

    def build(self, request, args, kwargs):
        """Returns a URI for this route.

        :param request:
            The current :class:`Request` object.
        :param args:
            Tuple of positional arguments to build the URI.
        :param kwargs:
            Dictionary of keyword arguments to build the URI.
        :returns:
            An absolute or relative URI.
        """
        raise NotImplementedError()

    def get_routes(self):
        """Generator to get all routes from a route.

        :yields:
            This route or all nested routes that it contains.
        """
        yield self

    def get_match_routes(self):
        """Generator to get all routes that can be matched from a route.

        Match routes must implement :meth:`match`.

        :yields:
            This route or all nested routes that can be matched.
        """
        if not self.build_only:
            yield self

    def get_build_routes(self):
        """Generator to get all routes that can be built from a route.

        Build routes must implement :meth:`build`.

        :yields:
            A tuple ``(name, route)`` for all nested routes that can be built.
        """
        if self.name is not None:
            yield self.name, self

#<----------------------------------------------------------------------------->

class SimpleRoute(BaseRoute):
    """A route that is compatible with webapp's routing mechanism.

    URI building is not implemented as webapp has rudimentar support for it,
    and this is the most unknown webapp feature anyway.
    """

    @cached_property
    def regex(self):
        """Lazy regex compiler."""
        if not self.uri_template.startswith('^'):
            self.uri_template = '^' + self.uri_template

        if not self.uri_template.endswith('$'):
            self.uri_template += '$'

        return re.compile(self.uri_template)

    def match(self, request):
        """Matches this route against the current request.

        .. seealso:: :meth:`BaseRoute.match`.
        """
        match = self.regex.match(urlunquote(request.path))
        if match:
            return self, match.groups(), {}

    def __repr__(self):
        return '<SimpleRoute({!r}, {!r})>'.format(self.uri_template, self.handler)

#<----------------------------------------------------------------------------->

class Route(BaseRoute):
    """A route definition that maps a URI path to a handler.

    The initial concept was based on Another Do-It-Yourself Framework, by
    Ian Bicking.
    """

    #: Default parameters values.
    defaults = None
    
    #: Sequence of allowed HTTP methods. If not set, all methods are allowed.
    methods = None
    
    #: Sequence of allowed URI schemes. If not set, all schemes are allowed.
    schemes = None
    
    # Lazy properties extracted from the route template.
    regex = None
    reverse_uri_template = None
    variables = None
    args_count = 0
    kwargs_count = 0

    def __init__(self, uri_template, handler=None, name=None, defaults=None,
                 build_only=False, handler_method=None, methods=None,
                 schemes=None):
        """Initializes this route.

        :param uri_template:
            A route template to match against the request path. A template
            can have variables enclosed by ``<>`` that define a name, a
            regular expression or both. Examples:

              =================  ==================================
              Format             Example
              =================  ==================================
              ``<name>``         ``'/blog/<year>/<month>'``
              ``<:regex>``       ``'/blog/<:\d{4}>/<:\d{2}>'``
              ``<name:regex>``   ``'/blog/<year:\d{4}>/<month:\d{2}>'``
              =================  ==================================

            The same template can mix parts with name, regular expression or
            both.

            If the name is set, the value of the matched regular expression
            is passed as keyword argument to the handler. Otherwise it is
            passed as positional argument.

            If only the name is set, it will match anything except a slash.
            So these routes are equivalent::

                Route('/<user_id>/settings', handler=SettingsHandler, name='user-settings')
                Route('/<user_id:[^/]+>/settings', handler=SettingsHandler, name='user-settings')

            .. note::
               The handler only receives ``*args`` if no named variables are
               set. Otherwise, the handler only receives ``**kwargs``. This
               allows you to set regular expressions that are not captured:
               just mix named and unnamed variables and the handler will
               only receive the named ones.

        :param handler:
            A callable or string in dotted notation to be lazily imported,
            e.g., ``'my.module.MyHandler'`` or ``'my.module.my_function'``.
            It is possible to define a method if the callable is a class,
            separating it by a colon: ``'my.module.MyHandler:my_method'``.
            This is a shortcut and has the same effect as defining the
            `handler_method` parameter.
        :param name:
            The name of this route, used to build URIs based on it.
        :param defaults:
            Default or extra keywords to be returned by this route. Values
            also present in the route variables are used to build the URI
            when they are missing.
        :param build_only:
            If True, this route never matches and is used only to build URIs.
        :param handler_method:
            The name of a custom handler method to be called, in case `handler`
            is a class. If not defined, the default behavior is to call the
            handler method correspondent to the HTTP request method in lower
            case (e.g., `get()`, `post()` etc).
        :param methods:
            A sequence of HTTP methods. If set, the route will only match if
            the request method is allowed.
        :param schemes:
            A sequence of URI schemes, e.g., ``['http']`` or ``['https']``.
            If set, the route will only match requests with these schemes.
        """
        super(Route, self).__init__(uri_template, handler=handler, name=name,
                                    build_only=build_only)
        
        self.defaults = defaults or {}
        self.methods = methods
        self.schemes = schemes
        
        if isinstance(handler, _basestring) and ':' in handler:
            if handler_method:
                error_msg = "You cannot define a method handler in {!r} using \
                a colon (:) if the handler_method keyword is defined in the \
                Route.".format(handler)
                raise ValueError(error_msg)

            else:
                self.handler, self.handler_method = handler.rsplit(':', 1)
        else:
            self.handler_method = handler_method

    @cached_property
    def regex(self):
        """Lazy route template parser."""
        regex, self.reverse_uri_template, self.args_count, self.kwargs_count, \
            self.variables = _parse_route_template(self.uri_template,
                                                   default_sufix='[^/]+')
        return regex

    def match(self, request):
        """Matches this route against the current request.

        :raises:
            ``exc.HTTPMethodNotAllowed`` if the route defines :attr:`methods`
            and the request method isn't allowed.

        .. seealso:: :meth:`BaseRoute.match`.
        """
        match = self.regex.match(urlunquote(request.path))
        if not match or self.schemes and request.scheme not in self.schemes:
            return None

        if self.methods and request.method not in self.methods:
            # This will be caught by the router, so routes with different
            # methods can be tried.
            raise exc.HTTPMethodNotAllowed()

        args, kwargs = _get_route_variables(match, self.defaults.copy())
        return self, args, kwargs

    def build(self, request, args, kwargs):
        """Returns a URI for this route.

        .. seealso:: :meth:`Router.build`.
        """
        scheme = kwargs.pop('_scheme', None)
        netloc = kwargs.pop('_netloc', None)
        anchor = kwargs.pop('_fragment', None)
        full = kwargs.pop('_full', False) and not scheme and not netloc

        if full or scheme or netloc:
            netloc = netloc or request.host
            scheme = scheme or request.scheme

        path, query = self._build(args, kwargs)
        return _urlunsplit(scheme, netloc, path, query, anchor)

    def _build(self, args, kwargs):
        """Returns the URI path for this route.

        :returns:
            A tuple ``(path, kwargs)`` with the built URI path and extra
            keywords to be used as URI query arguments.
        """
        # Access self.regex just to set the lazy properties.
        regex = self.regex
        variables = self.variables
        if self.args_count:
            for index, value in enumerate(args):
                key = '__{:d}__'.format(index)
                if key in variables:
                    kwargs[key] = value

        values = {}
        for name, regex in iter(variables.items()):
            value = kwargs.pop(name, self.defaults.get(name))
            if not value:
                error_msg = 'Missing argument "{}" to build URI.'.format(name.strip('_'))
                raise KeyError(error_msg)

            if not isinstance(value, _basestring):
                value = str(value)

            if not regex.match(value):
                error_msg = 'URI buiding error: Value "{}" is not supported \
                    for argument "{}".'.format(value, name.strip('_'))
                raise ValueError(error_msg)

            values[name] = value

        return (self.reverse_uri_template % values, kwargs)

    def __repr__(self):
        rep = '<Route({!r}, {!r}, name={!r}, defaults={!r}, build_only={!r})>'\
            .format(self.uri_template, self.handler, self.name, self.defaults,
            self.build_only)
        return rep

#<----------------------------------------------------------------------------->

class Router(object):
    """A URI router used to match, dispatch and build URIs."""

    #: Class used when the route is set as a tuple.
    route_class = SimpleRoute
    
    #: All routes that can be matched.
    match_routes = None
    
    #: All routes that can be built.
    build_routes = None
    
    #: Handler classes imported lazily.
    handlers = None

    def __init__(self, routes=None):
        """Initializes the router.

        :param routes:
            A sequence of :class:`Route` instances or, for simple routes,
            tuples ``(regex, handler)``.
        """
        self.match_routes = []
        self.build_routes = {}
        self.handlers = {}
        if routes:
            for route in routes:
                self.add(route)

    def add(self, route):
        """Adds a route to this router.

        :param route:
            A :class:`Route` instance or, for simple routes, a tuple
            ``(regex, handler)``.
        """
        if isinstance(route, tuple):
            # Exceptional case: simple routes defined as a tuple.
            route = self.route_class(*route)

        for r in route.get_match_routes():
            self.match_routes.append(r)

        for name, r in route.get_build_routes():
            self.build_routes[name] = r

    def set_matcher(self, func):
        """Sets the function called to match URIs.

        :param func:
            A function that receives ``(router, request)`` and returns
            a tuple ``(route, args, kwargs)`` if any route matches, or
            raise ``exc.HTTPNotFound`` if no route matched or
            ``exc.HTTPMethodNotAllowed`` if a route matched but the HTTP
            method was not allowed.
        """
        # Functions are descriptors, so bind it to this instance with __get__.
        self.match = func.__get__(self, self.__class__)

    def set_builder(self, func):
        """Sets the function called to build URIs.

        :param func:
            A function that receives ``(router, request, name, args, kwargs)``
            and returns a URI.
        """
        self.build = func.__get__(self, self.__class__)

    def set_dispatcher(self, func):
        """Sets the function called to dispatch the handler.

        :param func:
            A function that receives ``(router, request, response)``
            and returns the value returned by the dispatched handler.
        """
        self.dispatch = func.__get__(self, self.__class__)

    def set_adapter(self, func):
        """Sets the function that adapts loaded handlers for dispatching.

        :param func:
            A function that receives ``(router, handler)`` and returns a
            handler callable.
        """
        self.adapt = func.__get__(self, self.__class__)

    def default_matcher(self, request):
        """Matches all routes against a request object.

        The first one that matches is returned.

        :param request:
            A :class:`Request` instance.
        :returns:
            A tuple ``(route, args, kwargs)`` if a route matched, or None.
        :raises:
            ``exc.HTTPNotFound`` if no route matched or
            ``exc.HTTPMethodNotAllowed`` if a route matched but the HTTP
            method was not allowed.
        """
        method_not_allowed = False
        for route in self.match_routes:
            try:
                match = route.match(request)
                if match:
                    return match
            except exc.HTTPMethodNotAllowed:
                method_not_allowed = True

        if method_not_allowed:
            raise exc.HTTPMethodNotAllowed()

        raise exc.HTTPNotFound()

    def default_builder(self, request, name, args, kwargs):
        """Returns a URI for a named :class:`Route`.

        :param request:
            The current :class:`Request` object.
        :param name:
            The route name.
        :param args:
            Tuple of positional arguments to build the URI. All positional
            variables defined in the route must be passed and must conform
            to the format set in the route. Extra arguments are ignored.
        :param kwargs:
            Dictionary of keyword arguments to build the URI. All variables
            not set in the route default values must be passed and must
            conform to the format set in the route. Extra keywords are
            appended as a query string.

            A few keywords have special meaning:

            - **_full**: If True, builds an absolute URI.
            - **_scheme**: URI scheme, e.g., `http` or `https`. If defined,
              an absolute URI is always returned.
            - **_netloc**: Network location, e.g., `www.google.com`. If
              defined, an absolute URI is always returned.
            - **_fragment**: If set, appends a fragment (or "anchor") to the
              generated URI.
        :returns:
            An absolute or relative URI.
        """
        route = self.build_routes.get(name)
        if route is None:
            raise KeyError('Route named {!r} is not defined.'.format(name))

        return route.build(request, args, kwargs)

    def default_dispatcher(self, request, response):
        """Dispatches a handler.

        :param request:
            A :class:`Request` instance.
        :param response:
            A :class:`Response` instance.
        :raises:
            ``exc.HTTPNotFound`` if no route matched or
            ``exc.HTTPMethodNotAllowed`` if a route matched but the HTTP
            method was not allowed.
        :returns:
            The returned value from the handler.
        """
        route, args, kwargs = rv = self.match(request)
        request.route, request.route_args, request.route_kwargs = rv

        if route.handler_adapter is None:
            handler = route.handler
            if isinstance(handler, _basestring):
                if handler not in self.handlers:
                    self.handlers[handler] = handler = import_string(handler)
                else:
                    handler = self.handlers[handler]

            route.handler_adapter = self.adapt(handler)

        return route.handler_adapter(request, response)

    def default_adapter(self, handler):
        """Adapts a handler for dispatching.

        Because handlers use or implement different dispatching mechanisms,
        they can be wrapped to use a unified API for dispatching.
        This way webapp2 can support, for example, a :class:`RequestHandler`
        class and function views or, for compatibility purposes, a
        ``webapp.RequestHandler`` class. The adapters follow the same router
        dispatching API but dispatch each handler type differently.

        :param handler:
            A handler callable.
        :returns:
            A wrapped handler callable.
        """
        if inspect.isclass(handler):
            # Default, compatible with webbow.request.RequestHandler.
            adapter = WebToolsHandlerAdapter
        else:
            # A "view" function.
            adapter = BaseHandlerAdapter

        return adapter(handler)

    def __repr__(self):
        routes = self.match_routes + [v for k, v in \
            iter(self.build_routes.items()) if v not in self.match_routes]

        return '<Router({!r})>'.format(routes)

    # Default matcher, builder, dispatcher and adapter.
    match = default_matcher
    build = default_builder
    dispatch = default_dispatcher
    adapt = default_adapter