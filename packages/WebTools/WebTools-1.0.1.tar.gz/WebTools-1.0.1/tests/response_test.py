#!/usr/bin/python
# -*- coding: utf-8 -*-

import webtools
import test_base
import sys

if sys.version < '3':
    # python 2.7 compatibility
    _unicode = unicode

else:
    # python 3.0 compatibility
    _unicode = str

#<----------------------------------------------------------------------------->

class TestResponse(test_base.BaseTestCase):
    def test_write(self):
        var_1 = 'something'
        var_2 = 'foo'
        var_3 = _unicode('bar')

        rsp = webtools.Response()
        rsp.write(var_1)
        rsp.write(var_2)
        rsp.write(var_3)
        self.assertEqual(rsp.text, '{}foobar'.format(var_1))

        rsp = webtools.Response()
        rsp.write(var_1)
        rsp.write(var_3)
        rsp.write(var_2)
        self.assertEqual(rsp.text, '{}barfoo'.format(var_1))

        rsp = webtools.Response()
        rsp.write(var_2)
        rsp.write(var_1)
        rsp.write(var_3)
        self.assertEqual(rsp.text, 'foo{}bar'.format(var_1))

        rsp = webtools.Response()
        rsp.write(var_2)
        rsp.write(var_3)
        rsp.write(var_1)
        self.assertEqual(rsp.text, 'foobar{}'.format(var_1))

        rsp = webtools.Response()
        rsp.write(var_3)
        rsp.write(var_1)
        rsp.write(var_2)
        self.assertEqual(rsp.text, 'bar{}foo'.format(var_1))

        rsp = webtools.Response()
        rsp.write(var_3)
        rsp.write(var_2)
        rsp.write(var_1)
        self.assertEqual(rsp.text, 'barfoo{}'.format(var_1))

    def test_write2(self):
        rsp = webtools.Response()
        rsp.write('foo')
        self.assertEqual(rsp.text, 'foo')
        self.assertEqual(rsp.charset, 'UTF-8')

    def test_status(self):
        rsp = webtools.Response()

        self.assertEqual(rsp.status, '200 OK')
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.status_message, 'OK')

        rsp.status = _unicode('200 OK')
        self.assertEqual(rsp.status, '200 OK')
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.status_message, 'OK')

        rsp.status = 404
        self.assertEqual(rsp.status, '404 Not Found')
        self.assertEqual(rsp.status_int, 404)
        self.assertEqual(rsp.status_message, 'Not Found')

        rsp.status = '403 Wooo'
        self.assertEqual(rsp.status, '403 Wooo')
        self.assertEqual(rsp.status_int, 403)
        self.assertEqual(rsp.status_message, 'Wooo')

        rsp.status_int = 500
        self.assertEqual(rsp.status, '500 Internal Server Error')
        self.assertEqual(rsp.status_int, 500)
        self.assertEqual(rsp.status_message, 'Internal Server Error')

        self.assertRaises(TypeError, rsp._set_status, ())
    
    def test_get_all(self):
        rsp = webtools.Response()
        rsp.headers.add('Set-Cookie', 'foo=bar;')
        rsp.headers.add('Set-Cookie', 'baz=ding;')

        self.assertEqual(rsp.headers.get_all('set-cookie'),
            ['foo=bar;', 'baz=ding;'])

        rsp = webtools.Response()
        rsp.headers = {'Set-Cookie': 'foo=bar;'}
        self.assertEqual(rsp.headers.get_all('set-cookie'), ['foo=bar;'])

    def test_add_header(self):
        rsp = webtools.Response()
        rsp.headers.add_header('Content-Disposition', 'attachment',
            filename='bud.gif')
        self.assertEqual(rsp.headers.get('content-disposition'),
            'attachment; filename="bud.gif"')

        rsp = webtools.Response()
        rsp.headers.add_header('Content-Disposition', 'attachment',
            filename=None)
        self.assertEqual(rsp.headers.get('content-disposition'),
            'attachment; filename')

        rsp = webtools.Response()
        rsp.headers.add_header('Set-Cookie', '', foo='')
        self.assertEqual(rsp.headers.get_all('set-cookie'), ['; foo'])

        rsp = webtools.Response()
        rsp.headers.add_header('Set-Cookie', '', foo=';')
        self.assertEqual(rsp.headers.get_all('set-cookie'), ['; foo=";"'])

    # Tests from Python source: wsgiref.headers.Headers
    def test_headers_MappingInterface(self):
        rsp = webtools.Response()
        test = [('x','y')]
        self.assertEqual(len(rsp.headers), 2)
        rsp.headers = test[:]
        self.assertEqual(len(rsp.headers), 1)
        self.assertEqual(list(rsp.headers.keys()), ['x'])
        self.assertEqual(list(rsp.headers.values()), ['y'])
        self.assertEqual(list(rsp.headers.items()), test)
        rsp.headers = test
        self.assertFalse(rsp.headers.items() is test)  # must be copy!

        rsp = webtools.Response()
        h = rsp.headers
        # this doesn't raise an error in wsgiref.headers.Headers
        # del h['foo']

        h['Foo'] = 'bar'
        for m in h.has_key, h.__contains__, h.get, h.get_all, h.__getitem__:
            self.assertTrue(m('foo'))
            self.assertTrue(m('Foo'))
            self.assertTrue(m('FOO'))
            # this doesn't raise an error in wsgiref.headers.Headers
            # self.assertFalse(m('bar'))

        self.assertEqual(h['foo'],'bar')
        h['foo'] = 'baz'
        self.assertEqual(h['FOO'],'baz')
        self.assertEqual(h.get_all('foo'),['baz'])

        self.assertEqual(h.get("foo","whee"), "baz")
        self.assertEqual(h.get("zoo","whee"), "whee")
        self.assertEqual(h.setdefault("foo","whee"), "baz")
        self.assertEqual(h.setdefault("zoo","whee"), "whee")
        self.assertEqual(h["foo"],"baz")
        self.assertEqual(h["zoo"],"whee")

    def test_headers_RequireList(self):
        def set_headers():
            rsp = webtools.Response()
            rsp.headers = 'foo'
            return rsp.headers

        self.assertRaises(TypeError, set_headers)

    def test_headers_Extras(self):
        rsp = webtools.Response()
        rsp.headers = []
        h = rsp.headers
        self.assertEqual(str(h),'\r\n')

        h.add_header('foo','bar',baz="spam")
        self.assertEqual(h['foo'], 'bar; baz="spam"')
        self.assertEqual(str(h),'foo: bar; baz="spam"\r\n\r\n')

        h.add_header('Foo','bar',cheese=None)
        self.assertEqual(h.get_all('foo'),
            ['bar; baz="spam"', 'bar; cheese'])

        self.assertEqual(str(h),
            'foo: bar; baz="spam"\r\n'
            'Foo: bar; cheese\r\n'
            '\r\n'
        )

    def test_write_json(self):
        rsp = webtools.Response()
        rsp.write_json({'foo': 'bar'})
        self.assertEqual(rsp.text, '{"foo": "bar"}')
        self.assertEqual(rsp.content_type, 'application/json')

        rsp = webtools.Response()
        rsp.write_json([1, 2, 3])
        self.assertEqual(rsp.text, '[1, 2, 3]')
        self.assertEqual(rsp.content_type, 'application/json')


class TestReturnResponse(test_base.BaseTestCase):
    def test_function_that_returns_response(self):
        def myfunction(request, *args, **kwargs):
            return webtools.Response('Hello, custom response world!')

        app = webtools.WSGIApplication([
            ('/', myfunction),
        ])

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello, custom response world!')

    def test_function_that_returns_string(self):
        def myfunction(request, *args, **kwargs):
            return 'Hello, custom response world!'

        app = webtools.WSGIApplication([
            ('/', myfunction),
        ])

        def custom_dispatcher(router, request, response):
            response_str = router.default_dispatcher(request, response)
            return request.app.response_class(response_str)

        app.router.set_dispatcher(custom_dispatcher)

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello, custom response world!')

    def test_function_that_returns_tuple(self):
        def myfunction(request, *args, **kwargs):
            return 'Hello, custom response world!', 404

        app = webtools.WSGIApplication([
            ('/', myfunction),
        ])

        def custom_dispatcher(router, request, response):
            response_tuple = router.default_dispatcher(request, response)
            return request.app.response_class(*response_tuple)

        app.router.set_dispatcher(custom_dispatcher)

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 404)
        self.assertEqual(rsp.text, 'Hello, custom response world!')

    def test_handle_exception_that_returns_response(self):
        class HomeHandler(webtools.RequestHandler):
            def get(self, **kwargs):
                raise TypeError()

        app = webtools.WSGIApplication([
            webtools.Route('/', HomeHandler, name='home'),
        ])
        app.error_handlers[500] = 'resources.handlers.handle_exception'

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello, custom response world!')

    def test_return_is_not_wsgi_app(self):
        class HomeHandler(webtools.RequestHandler):
            def get(self, **kwargs):
                return ''

        app = webtools.WSGIApplication([
            webtools.Route('/', HomeHandler, name='home'),
        ], debug=False)

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 500)


if __name__ == '__main__':
    test_base.main()
