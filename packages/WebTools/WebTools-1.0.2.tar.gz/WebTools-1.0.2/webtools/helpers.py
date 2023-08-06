#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

if sys.version < '3':
    # python 2.7 compatibility
    from urlparse import urljoin

else:
    # python 3.0 compatibility
    from urllib.parse import urljoin

from .wsgi import WSGIApplication
from .utils.http import abort as _abort

#<----------------------------------------------------------------------------->

def get_app():
    """Returns the active app instance.

    :returns:
        A :class:`WSGIApplication` instance.
    """
    return WSGIApplication.app

#<----------------------------------------------------------------------------->

def get_request():
    """Returns the active request instance.

    :returns:
        A :class:`Request` instance.
    """
    return WSGIApplication.request

#<----------------------------------------------------------------------------->

def uri_for(_name, _request=None, *args, **kwargs):
    """A standalone uri_for version that can be passed to templates.

    .. seealso:: :meth:`Router.build`.
    """
    request = _request or get_request()
    return request.app.router.build(request, _name, args, kwargs)

#<----------------------------------------------------------------------------->

def redirect(uri, permanent=False, abort=False, code=None, body=None,
             request=None, response=None):
    """Issues an HTTP redirect to the given relative URI.

    This won't stop code execution unless **abort** is True. A common
    practice is to return when calling this method::

        return redirect('/some-path')

    :param uri:
        A relative or absolute URI (e.g., ``'../flowers.html'``).
    :param permanent:
        If True, uses a 301 redirect instead of a 302 redirect.
    :param abort:
        If True, raises an exception to perform the redirect.
    :param code:
        The redirect status code. Supported codes are 301, 302, 303, 305,
        and 307.  300 is not supported because it's not a real redirect
        and 304 because it's the answer for a request with defined
        ``If-Modified-Since`` headers.
    :param body:
        Response body, if any.
    :param request:
        Optional request object. If not set, uses :func:`get_request`.
    :param response:
        Optional response object. If not set, a new response is created.
    :returns:
        A :class:`Response` instance.
    """
    if uri.startswith(('.', '/')):
        request = request or get_request()
        uri = str(urljoin(request.url, uri))

    if code is None:
        if permanent:
            code = 301
        else:
            code = 302

    assert code in (301, 302, 303, 305, 307), \
        'Invalid redirect status code.'

    if abort:
        _abort(code, headers=[('Location', uri)])

    if response is None:
        request = request or get_request()
        response = request.app.response_class()
    else:
        response.clear()

    response.headers['Location'] = uri
    response.status = code
    if body is not None:
        response.write(body)

    return response

#<----------------------------------------------------------------------------->

def redirect_to(_name, _permanent=False, _abort=False, _code=None,
                _body=None, _request=None, _response=None, *args, **kwargs):
    """Convenience function mixing :func:`redirect` and :func:`uri_for`.

    Issues an HTTP redirect to a named URI built using :func:`uri_for`.

    :param _name:
        The route name to redirect to.
    :param args:
        Positional arguments to build the URI.
    :param kwargs:
        Keyword arguments to build the URI.
    :returns:
        A :class:`Response` instance.

    The other arguments are described in :func:`redirect`.
    """
    uri = uri_for(_name, _request=_request, *args, **kwargs)
    return redirect(uri, permanent=_permanent, abort=_abort, code=_code,
                    body=_body, request=_request, response=_response)