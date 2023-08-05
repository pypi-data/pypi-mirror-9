#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
HTTP response objects.  Ported from webapp2, refactored to
support Python versions > 2.7, 3.0
"""
import json
import webob

from webob.headers import ResponseHeaders as BaseResponseHeaders
from .utils.http import status_reasons
from .utils.strings import _basestring, _unicode, _bytes

#<----------------------------------------------------------------------------->

class ResponseHeaders(BaseResponseHeaders):
    """Implements methods from ``wsgiref.headers.Headers``, used by webtools."""

    get_all = BaseResponseHeaders.getall

    def add_header(self, _name, _value, **_params):
        """Extended header setting.

        _name is the header field to add.  keyword arguments can be used to set
        additional parameters for the header field, with underscores converted
        to dashes.  Normally the parameter will be added as key="value" unless
        value is None, in which case only the key will be added.

        Example::

            h.add_header('content-disposition', 'attachment', filename='bud.gif')

        Note that unlike the corresponding 'email.message' method, this does
        *not* handle '(charset, language, value)' tuples: all values must be
        strings or None.
        """
        parts = []
        if _value is not None:
            parts.append(_value)

        for k, v in _params.items():
            k = k.replace('_', '-')
            if v is not None and len(v) > 0:
                v = v.replace('\\', '\\\\').replace('"', r'\"')
                parts.append('{}="{}"'.format(k, v))
            else:
                parts.append(k)

        self.add(_name, '; '.join(parts))

    def __str__(self):
        """Returns the formatted headers ready for HTTP transmission."""
        str_parts = ['{}: {}'.format(*v) for v in self.items()] + ['', '']
        return '\r\n'.join(str_parts)

#<----------------------------------------------------------------------------->

class Response(webob.Response):
    """Abstraction for an HTTP response."""
        
    #<------------------------------------------------------------------------->

    def _set_status(self, value):
        """The status string, including code and message."""
        message = None
        
        if isinstance(value, int):
            code = value
        else:
            if not isinstance(value, _basestring):
                error_msg = 'You must set status to a string or integer (not {})'
                raise TypeError(error_msg.format(type(value)))
            
            parts = value.split(' ', 1)
            code = int(parts[0])
            
            if len(parts) == 2:
                message = parts[1]

        message = message or Response.http_status_message(code)
        self._status = '{:d} {}'.format(code, message)

    def _get_status(self):
        return self._status

    status = property(_get_status, _set_status, doc=_set_status.__doc__)

    #<------------------------------------------------------------------------->

    def set_status(self, code, message=None):
        """Sets the HTTP status code of this response.

        :param code:
            The HTTP status string to use
        :param message:
            A status string. If none is given, uses the default from the
            HTTP/1.1 specification.
        """
        if message:
            self.status = '{:d} {}'.format(code, message)
        else:
            self.status = code

    #<------------------------------------------------------------------------->

    def _get_status_message(self):
        """The response status message, as a string."""
        return self.status.split(' ', 1)[1]

    def _set_status_message(self, message):
        self.status = '{:d} {}'.format(self.status_int, message)

    status_message = property(_get_status_message, _set_status_message,
                              doc=_get_status_message.__doc__)

    #<------------------------------------------------------------------------->

    def _get_headers(self):
        """The headers as a dictionary-like object."""
        if self._headers is None:
            self._headers = ResponseHeaders.view_list(self.headerlist)

        return self._headers

    def _set_headers(self, value):
        if hasattr(value, 'items'):
            value = value.items()
        elif not isinstance(value, list):
            raise TypeError('Response headers must be a list or dictionary.')

        self.headerlist = value
        self._headers = None

    headers = property(_get_headers, _set_headers, doc=_get_headers.__doc__)

    #<------------------------------------------------------------------------->

    def clear(self):
        """Clears all data written to the output stream so that it is empty."""
        self.body = b''

    #<------------------------------------------------------------------------->

    def write_json(self, value):
        """Writes the value to the response body as a JSON encoded string. Also
        sets the response content type to application/json. """

        self.content_type = 'application/json'
        self.write(json.dumps(value))
    
    #<------------------------------------------------------------------------->

    @staticmethod
    def http_status_message(code):
        """Returns the default HTTP status message for the given code.

        :param code:
            The HTTP code for which we want a message.
        """
        message = status_reasons.get(code)
        if not message:
            raise KeyError('Invalid HTTP status code: {:d}'.format(code))

        return message