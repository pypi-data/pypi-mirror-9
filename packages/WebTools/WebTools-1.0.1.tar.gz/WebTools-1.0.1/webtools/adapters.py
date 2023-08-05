#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
HTTP handler adapters.  Ported from webapp2, refactored to
support Python versions > 2.7, 3.0
"""

#<----------------------------------------------------------------------------->

class BaseHandlerAdapter(object):
    """A basic adapter to dispatch a handler.

    This is used when the handler is a simple function: it just calls the
    handler and returns the resulted response.
    """

    #: The handler to be dispatched.
    handler = None

    def __init__(self, handler):
        self.handler = handler

    def __call__(self, request, response):
        # The handler only receives *args if no named variables are set.
        args, kwargs = request.route_args, request.route_kwargs
        if kwargs:
            args = ()

        return self.handler(request, *args, **kwargs)

#<----------------------------------------------------------------------------->

class WebToolsHandlerAdapter(BaseHandlerAdapter):
    """An adapter to dispatch a ``webbox.request.RequestHandler``.

    The handler is constructed then ``dispatch()`` is called.
    """

    def __call__(self, request, response):
        handler = self.handler(request, response)
        return handler.dispatch()