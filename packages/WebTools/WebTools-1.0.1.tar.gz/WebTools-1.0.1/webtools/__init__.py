#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
WebTools is web application framework built on top of WebOb.  WebTools started as
a fork of the webapp2 framework built for Google's App Engine hosting environment.
WebTools is release under the Apache Version 2.0 license.
"""


__version_info__ = (1, 0, 1)
__version__ = '.'.join(str(n) for n in __version_info__)
__release__ = '{} {}'.format(__version__, 'Beta')

#<----------------------------------------------------------------------------->

from .route import Route
from .response import Response
from .request import Request
from .handlers import (
    RequestHandler, 
    RedirectHandler
    )
from .wsgi import WSGIApplication
from .helpers import (
    get_app, 
    get_request, 
    uri_for, 
    redirect, 
    redirect_to
    )
from .utils.http import HTTPException

#<----------------------------------------------------------------------------->

__all__ = ['Route', 'Request', 'Response', 'RequestHandler', 'RedirectHandler', 
    'WSGIApplication', 'HTTPException', 'get_app', 'get_request', 'uri_for', 
    'redirect', 'redirect_to']