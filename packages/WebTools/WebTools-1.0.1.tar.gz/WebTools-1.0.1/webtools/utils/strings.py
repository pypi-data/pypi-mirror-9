#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
String functions for converting values to unicode and/or byte strings
"""

import sys

if sys.version < '3':
    # python 2.7 compatibility
    _basestring = basestring
    _unicode = unicode
    _bytes = str

    from .p2 import raise_with_traceback

else:
    # python 3.0 compatibility
    _basestring = str
    _unicode = str
    _bytes = bytes

    from .p3 import raise_with_traceback

#<----------------------------------------------------------------------------->

def _to_utf8(value):
    """Encodes a unicode value to UTF-8 if not yet encoded."""
    if isinstance(value, _unicode):
        return value.encode('utf-8')

    return value

#<----------------------------------------------------------------------------->

"""
Functions for importing modules defined as strings.  Ported from webapp2, 
refactored to support Python versions > 2.7, 3.0
"""

#<----------------------------------------------------------------------------->

class ImportStringError(Exception):
    """Provides information about a failed :func:`import_string` attempt."""

    #: String in dotted notation that failed to be imported.
    import_name = None
    
    #: Wrapped exception.
    exception = None

    def __init__(self, import_name, exception):
        self.import_name = import_name
        self.exception = exception
        msg = ('import_string() failed for {!r}. Possible reasons are:\n\n'
               '- missing __init__.py in a package;\n'
               '- package or module path not included in sys.path;\n'
               '- duplicated package or module name taking precedence in '
               'sys.path;\n'
               '- missing module, class, function or variable;\n\n'
               'Original exception:\n\n{}: {}\n\n'
               'Debugged import:\n\n{}')
        name = ''
        tracked = []
        for part in import_name.split('.'):
            name += (name and '.') + part
            imported = import_string(name, silent=True)
            if imported:
                tracked.append((name, imported.__file__))
            else:
                track = ['- {!r} found in {!r}.'.format(rv) for rv in tracked]
                track.append('- {!r} not found.'.format(name))
                msg = msg.format(import_name, exception.__class__.__name__,
                             str(exception), '\n'.join(track))
                break

        Exception.__init__(self, msg)

#<----------------------------------------------------------------------------->

def import_string(import_name, silent=False):
    """Imports an object based on a string in dotted notation.

    Simplified version of the function with same name from `Werkzeug`_.

    :param import_name:
        String in dotted notation of the object to be imported.
    :param silent:
        If True, import or attribute errors are ignored and None is returned
        instead of raising an exception.
    :returns:
        The imported object.
    """
    
    try:
        if '.' in import_name:
            module, obj = import_name.rsplit('.', 1)
            return getattr(__import__(module, None, None, [obj]), obj)
        else:
            return __import__(import_name)
    except (ImportError, AttributeError) as e:
        if not silent:
            raise_with_traceback(ImportStringError(import_name, e))