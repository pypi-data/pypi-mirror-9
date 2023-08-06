#!/usr/bin/python
# -*- coding: utf-8 -*-

from webob import exc
from webob.util import status_reasons

#<----------------------------------------------------------------------------->

# Set same default messages from webapp plus missing ones.
_webtools_status_reasons = {
    203: 'Non-Authoritative Information',
    302: 'Moved Temporarily',
    306: 'Unused',
    408: 'Request Time-out',
    414: 'Request-URI Too Large',
    504: 'Gateway Time-out',
    505: 'HTTP Version not supported',
}

status_reasons.update(_webtools_status_reasons)

for code, message in iter(_webtools_status_reasons.items()):
    cls = exc.status_map.get(code)
    if cls:
        cls.title = message

#<----------------------------------------------------------------------------->

HTTPException = exc.HTTPException

#<----------------------------------------------------------------------------->

def abort(code, *args, **kwargs):
    """Raises an ``HTTPException``.

    :param code:
        An integer that represents a valid HTTP status code.
    :param args:
        Positional arguments to instantiate the exception.
    :param kwargs:
        Keyword arguments to instantiate the exception.
    """
    cls = exc.status_map.get(code)
    if not cls:
        raise KeyError('No exception is defined for code {!r}.'.format(code))

    raise cls(*args, **kwargs)