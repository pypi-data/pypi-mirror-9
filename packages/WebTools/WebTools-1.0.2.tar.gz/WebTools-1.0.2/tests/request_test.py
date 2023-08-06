#!/usr/bin/python
# -*- coding: utf-8 -*-

import webtools
import test_base
import sys

if sys.version < '3':
    # python 2.7 compatibility
    _basestring = basestring
    _unicode = unicode
    _bytes = str
    
    from urllib import urlencode
    from cStringIO import StringIO

else:
    # python 3.0 compatibility
    _basestring = str
    _unicode = str
    _bytes = str

    from urllib.parse import urlencode
    from io import BytesIO as StringIO

#<----------------------------------------------------------------------------->

def _norm_req(s):
    return '\r\n'.join(s.strip().replace('\r','').split('\n'))

_test_req = """
POST /webob/ HTTP/1.0
Accept: */*
Cache-Control: max-age=0
Content-Type: multipart/form-data; boundary=----------------------------deb95b63e42a
Host: pythonpaste.org
User-Agent: UserAgent/1.0 (identifier-version) library/7.0 otherlibrary/0.8

------------------------------deb95b63e42a
Content-Disposition: form-data; name="foo"

foo
------------------------------deb95b63e42a
Content-Disposition: form-data; name="bar"; filename="bar.txt"
Content-type: application/octet-stream

these are the contents of the file 'bar.txt'

------------------------------deb95b63e42a--
"""

_test_req2 = """
POST / HTTP/1.0
Content-Length: 0

"""

_test_req = _norm_req(_test_req)
_test_req2 = _norm_req(_test_req2) + '\r\n'

#<----------------------------------------------------------------------------->

def add_POST(req, data):
    if data is None:
        return
    env = req.environ
    env['REQUEST_METHOD'] = 'POST'
    if hasattr(data, 'items'):
        data = data.items()
    if not isinstance(data, _bytes):
        data = urlencode(data)
    env['wsgi.input'] = StringIO(data.encode('utf-8'))
    env['webob.is_body_seekable'] = True
    env['CONTENT_LENGTH'] = str(len(data))
    env['CONTENT_TYPE'] = 'application/x-www-form-urlencoded'


class TestRequest(test_base.BaseTestCase):
    def test_get(self):
        req = webtools.Request.blank('/?1=2&1=3&3=4')
        add_POST(req, '5=6&7=8')

        res = req.get('1')
        self.assertEqual(res, '2')

        res = req.get('8')
        self.assertEqual(res, '')

        res = req.get('8', default_value='9')
        self.assertEqual(res, '9')

    def test_get_with_FieldStorage(self):
        # A valid request without a Content-Length header should still read
        # the full body.
        # Also test parity between as_string and from_string / from_file.
        import cgi
        req = webtools.Request.from_bytes(_test_req.encode('utf-8'))
        self.assertTrue(isinstance(req, webtools.Request))
        self.assertTrue(not repr(req).endswith('(invalid WSGI environ)>'))
        self.assertTrue('\n' not in req.http_version or '\r' in req.http_version)
        self.assertTrue(',' not in req.host)
        self.assertTrue(req.content_length is not None)
        self.assertEqual(req.content_length, 337)
        self.assertTrue('foo' in req.text)
        bar_contents = "these are the contents of the file 'bar.txt'\r\n"
        self.assertTrue(bar_contents in req.text)
        self.assertEqual(req.params['foo'], 'foo')
        bar = req.params['bar']
        self.assertTrue(isinstance(bar, cgi.FieldStorage))
        self.assertEqual(bar.type, 'application/octet-stream')
        bar.file.seek(0)
        self.assertEqual(bar.file.read(), bar_contents.encode('utf-8'))
        bar = req.get_all('bar')
        self.assertEqual(bar[0], bar_contents.encode('utf-8'))

        # out should equal contents, except for the Content-Length header,
        # so insert that.
        _test_req_copy = _test_req.replace('Content-Type',
                            'Content-Length: 337\r\nContent-Type')
        self.assertEqual(str(req), _test_req_copy)

        req2 = webtools.Request.from_bytes(_test_req2.encode('utf-8'))
        self.assertTrue('host' not in req2.headers)
        self.assertEqual(str(req2), _test_req2.rstrip())
        self.assertRaises(ValueError,
                          webtools.Request.from_bytes, _test_req2.encode('utf-8') + b'xx')

    def test_get_with_POST(self):
        req = webtools.Request.blank('/?1=2&1=3&3=4', POST={5: 6, 7: 8},
                                    unicode_errors='ignore')

        res = req.get('1')
        self.assertEqual(res, '2')

        res = req.get('8')
        self.assertEqual(res, '')

        res = req.get('8', default_value='9')
        self.assertEqual(res, '9')

    def test_arguments(self):
        req = webtools.Request.blank('/?1=2&3=4')
        add_POST(req, '5=6&7=8')

        res = req.arguments()
        res.sort() # sorts in place
        self.assertEqual(res, ['1', '3', '5', '7'])

    def test_get_range(self):
        req = webtools.Request.blank('/')
        res = req.get_range('1', min_value=None, max_value=None, default=None)
        self.assertEqual(res, None)

        req = webtools.Request.blank('/?1=2')
        res = req.get_range('1', min_value=None, max_value=None, default=0)
        self.assertEqual(res, 2)

        req = webtools.Request.blank('/?1=foo')
        res = req.get_range('1', min_value=1, max_value=99, default=100)
        self.assertEqual(res, 99)

    def test_issue_3426(self):
        """When the content-type is 'application/x-www-form-urlencoded' and
        POST data is empty the content-type is dropped by Google appengine.
        """
        req = webtools.Request.blank('/', environ={
            'REQUEST_METHOD': 'GET',
            'CONTENT_TYPE': 'application/x-www-form-urlencoded',
        })
        self.assertEqual(req.method, 'GET')
        self.assertEqual(req.content_type, 'application/x-www-form-urlencoded')

    def test_issue_5118(self):
        """Unable to read POST variables ONCE self.request.body is read."""
        
        import cgi
        req = webtools.Request.from_bytes(_test_req.encode('utf-8'))
        fieldStorage = req.POST.get('bar')
        self.assertTrue(isinstance(fieldStorage, cgi.FieldStorage))
        self.assertEqual(fieldStorage.type, 'application/octet-stream')
        # Double read.
        fieldStorage = req.POST.get('bar')
        self.assertTrue(isinstance(fieldStorage, cgi.FieldStorage))
        self.assertEqual(fieldStorage.type, 'application/octet-stream')
        # Now read the body.
        x = req.text
        fieldStorage = req.POST.get('bar')
        self.assertTrue(isinstance(fieldStorage, cgi.FieldStorage))
        self.assertEqual(fieldStorage.type, 'application/octet-stream')


if __name__ == '__main__':
    test_base.main()
