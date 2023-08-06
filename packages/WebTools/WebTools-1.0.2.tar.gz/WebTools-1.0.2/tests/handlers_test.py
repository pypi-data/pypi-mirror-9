#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import webtools
import test_base
import sys

if sys.version < '3':
    # python 2.7 compatibility
    _basestring = basestring
    _unicode = unicode
    _bytes = str
    
    from urllib import unquote_plus
    from cStringIO import StringIO

else:
    # python 3.0 compatibility
    _basestring = str
    _unicode = str
    _bytes = str

    from urllib.parse import unquote_plus
    from io import BytesIO as StringIO

#<----------------------------------------------------------------------------->


class BareHandler(object):
    def __init__(self, request, response):
        self.response = response
        response.write('I am not a RequestHandler but I work.')

    def dispatch(self):
        return self.response


class HomeHandler(webtools.RequestHandler):
    def get(self, **kwargs):
        self.response.write('home sweet home')

    def post(self, **kwargs):
        self.response.write('home sweet home - POST')


class MethodsHandler(HomeHandler):
    def put(self, **kwargs):
        self.response.write('home sweet home - PUT')

    def delete(self, **kwargs):
        self.response.write('home sweet home - DELETE')

    def head(self, **kwargs):
        self.response.write('home sweet home - HEAD')

    def trace(self, **kwargs):
        self.response.write('home sweet home - TRACE')

    def options(self, **kwargs):
        self.response.write('home sweet home - OPTIONS')


class RedirectToHandler(webtools.RequestHandler):
    def get(self, **kwargs):
        return self.redirect_to('route-test', _fragment='my-anchor', year='2010',
                                month='07', name='test', foo='bar')


class RedirectAbortHandler(webtools.RequestHandler):
    def get(self, **kwargs):
        self.redirect('/somewhere', abort=True)


class BrokenHandler(webtools.RequestHandler):
    def get(self, **kwargs):
        raise ValueError('booo!')


class BrokenButFixedHandler(BrokenHandler):
    def handle_exception(self, exception, debug_mode):
        # Let's fix it.
        self.response.set_status(200)
        self.response.write('that was close!')

def handle_401(request, response, exception):
    response.write('401 custom handler')
    response.set_status(401)

def handle_404(request, response, exception):
    response.write('404 custom handler')
    response.set_status(404)


def handle_405(request, response, exception):
    response.write('405 custom handler')
    response.set_status(405, 'Custom Error Message')
    response.headers['Allow'] = 'GET'


def handle_500(request, response, exception):
    response.write('500 custom handler')
    response.set_status(500)


class PositionalHandler(webtools.RequestHandler):
    def get(self, month, day, slug=None):
        self.response.write('%s:%s:%s' % (month, day, slug))


class HandlerWithError(webtools.RequestHandler):
    def get(self, **kwargs):
        self.response.write('bla bla bla bla bla bla')
        self.error(403)


class InitializeHandler(webtools.RequestHandler):
    def __init__(self):
        pass

    def get(self):
        self.response.write('Request method: %s' % self.request.method)


class WebDavHandler(webtools.RequestHandler):
    def version_control(self):
        self.response.write('Method: VERSION-CONTROL')

    def unlock(self):
        self.response.write('Method: UNLOCK')

    def propfind(self):
        self.response.write('Method: PROPFIND')

class HandlerWithEscapedArg(webtools.RequestHandler):
    def get(self, name):
        self.response.write(unquote_plus(name))

def get_redirect_url(handler, **kwargs):
    return handler.uri_for('methods')

# Test authorization

def custom_authorize_callable(handler):
    key = handler.request.route_kwargs['key']

    if key == 'good':
        return True
    else:
        return False

class AuthorizationHandler(webtools.RequestHandler):
    authorize = custom_authorize_callable
    authorize_methods = ['POST']

    def get(self, *args, **kwargs):
        self.response.write('You can read the content without authorizing')

    def post(self, *args, **kwargs):
        self.response.write('But you cannot post unless you are authorized')

# Test cache-control

class CacheControlHandler(webtools.RequestHandler):
    cache_control = 'max-age=3600'

    def get(self, *args, **kwargs):
        self.response.write('GET requests are cached by the client')

    def post(self, *args, **kwargs):
        self.response.write('But POST requests are not cached by the client')

# Create the app

app = webtools.WSGIApplication([
    ('/bare', BareHandler),
    webtools.Route('/', HomeHandler, name='home'),
    webtools.Route('/methods', MethodsHandler, name='methods'),
    webtools.Route('/broken', BrokenHandler),
    webtools.Route('/broken-but-fixed', BrokenButFixedHandler),
    webtools.Route('/<year:\d{4}>/<month:\d\d>/<name>', None, name='route-test'),
    webtools.Route('/<:\d\d>/<:\d{2}>/<:\w+>', PositionalHandler, name='positional'),
    webtools.Route('/redirect-me', webtools.RedirectHandler, defaults={'_uri': '/broken'}),
    webtools.Route('/redirect-me2', webtools.RedirectHandler, defaults={'_uri': get_redirect_url}),
    webtools.Route('/redirect-me3', webtools.RedirectHandler, defaults={'_uri': '/broken', '_permanent': False}),
    webtools.Route('/redirect-me4', webtools.RedirectHandler, defaults={'_uri': get_redirect_url, '_permanent': False}),
    webtools.Route('/redirect-me5', RedirectToHandler),
    webtools.Route('/redirect-me6', RedirectAbortHandler),
    webtools.Route('/lazy', 'resources.handlers.LazyHandler'),
    webtools.Route('/error', HandlerWithError),
    webtools.Route('/initialize', InitializeHandler),
    webtools.Route('/webdav', WebDavHandler),
    webtools.Route('/authorization/<key>', AuthorizationHandler),
    webtools.Route('/cache-control', CacheControlHandler),
    webtools.Route('/escape/<name:.*>', HandlerWithEscapedArg, 'escape'),
], debug=False)

DEFAULT_RESPONSE = """Status: 404 Not Found
content-type: text/html; charset=utf8
Content-Length: 52

404 Not Found

The resource could not be found.

   """

class TestHandler(test_base.BaseTestCase):
    def tearDown(self):
        super(TestHandler, self).tearDown()
        app.error_handlers = {}

    def test_200(self):
        rsp = app.get_response('/')
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home')

    def test_404(self):
        req = webtools.Request.blank('/nowhere')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 404)

    def test_405(self):
        req = webtools.Request.blank('/')
        req.method = 'PUT'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 405)
        self.assertEqual(rsp.headers.get('Allow'), 'GET, POST')

    def test_500(self):
        req = webtools.Request.blank('/broken')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 500)

    def test_500_but_fixed(self):
        req = webtools.Request.blank('/broken-but-fixed')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'that was close!')

    def test_501(self):
        # 501 Not Implemented
        req = webtools.Request.blank('/methods')
        req.method = 'FOOBAR'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 501)

    def test_lazy_handler(self):
        req = webtools.Request.blank('/lazy')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'I am a laaazy view.')

    def test_handler_with_error(self):
        req = webtools.Request.blank('/error')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 403)
        self.assertEqual(rsp.text, '')

    def test_debug_mode(self):
        app = webtools.WSGIApplication([
            webtools.Route('/broken', BrokenHandler),
        ], debug=True)

        req = webtools.Request.blank('/broken')
        self.assertRaises(ValueError, req.get_response, app)

    def test_custom_error_handlers(self):
        app.error_handlers = {
            401: handle_401,
            404: handle_404,
            405: handle_405,
            500: handle_500,
        }
        req = webtools.Request.blank('/nowhere')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 404)
        self.assertEqual(rsp.text, '404 custom handler')

        req = webtools.Request.blank('/')
        req.method = 'PUT'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status, '405 Custom Error Message')
        self.assertEqual(rsp.text, '405 custom handler')
        self.assertEqual(rsp.headers.get('Allow'), 'GET')

        req = webtools.Request.blank('/broken')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 500)
        self.assertEqual(rsp.text, '500 custom handler')

        req = webtools.Request.blank('/authorization/bad')
        req.method = 'POST'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 401)
        self.assertEqual(rsp.text, '401 custom handler')

    def test_methods(self):
        app.debug = True
        req = webtools.Request.blank('/methods')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home')

        req = webtools.Request.blank('/methods')
        req.method = 'POST'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home - POST')

        req = webtools.Request.blank('/methods')
        req.method = 'PUT'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home - PUT')

        req = webtools.Request.blank('/methods')
        req.method = 'DELETE'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home - DELETE')

        req = webtools.Request.blank('/methods')
        req.method = 'HEAD'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, '')

        req = webtools.Request.blank('/methods')
        req.method = 'OPTIONS'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home - OPTIONS')

        req = webtools.Request.blank('/methods')
        req.method = 'TRACE'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'home sweet home - TRACE')
        app.debug = False

    def test_positional(self):
        req = webtools.Request.blank('/07/31/test')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, '07:31:test')

        req = webtools.Request.blank('/10/18/wooohooo')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, '10:18:wooohooo')

    def test_redirect(self):
        req = webtools.Request.blank('/redirect-me')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 301)
        self.assertEqual(rsp.text, '')
        self.assertEqual(rsp.headers['Location'], 'http://localhost/broken')

    def test_redirect_with_callable(self):
        req = webtools.Request.blank('/redirect-me2')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 301)
        self.assertEqual(rsp.text, '')
        self.assertEqual(rsp.headers['Location'], 'http://localhost/methods')

    def test_redirect_not_permanent(self):
        req = webtools.Request.blank('/redirect-me3')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 302)
        self.assertEqual(rsp.text, '')
        self.assertEqual(rsp.headers['Location'], 'http://localhost/broken')

    def test_redirect_with_callable_not_permanent(self):
        req = webtools.Request.blank('/redirect-me4')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 302)
        self.assertEqual(rsp.text, '')
        self.assertEqual(rsp.headers['Location'], 'http://localhost/methods')

    def test_redirect_to(self):
        req = webtools.Request.blank('/redirect-me5')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 302)
        self.assertEqual(rsp.text, '')
        self.assertEqual(rsp.headers['Location'], 'http://localhost/2010/07/test?foo=bar#my-anchor')

    def test_authorization(self):
        req = webtools.Request.blank('/authorization/public')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)

        req = webtools.Request.blank('/authorization/good')
        req.method = 'POST'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)

        req = webtools.Request.blank('/authorization/bad')
        req.method = 'POST'
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 401)

    def test_cache_control(self):
        req = webtools.Request.blank('/cache-control')
        rsp = req.get_response(app)
        self.assertEqual(rsp.headers.get('Cache-Control'), 'max-age=3600')

        req = webtools.Request.blank('/cache-control')
        req.method = 'POST'
        rsp = req.get_response(app)
        self.assertEqual(rsp.headers.get('Cache-Control'), 'max-age=0, no-cache, no-store')

    def test_redirect_abort(self):
        req = webtools.Request.blank('/redirect-me6')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 302)
        self.assertEqual(rsp.text, """302 Moved Temporarily

The resource was found at http://localhost/somewhere; you should be redirected automatically.  """)
        self.assertEqual(rsp.headers['Location'], 'http://localhost/somewhere')

    def test_run(self):
        os.environ['REQUEST_METHOD'] = 'GET'

        app.run()
        #self.assertEqual(sys.stdout.read(), DEFAULT_RESPONSE)

    def test_run_bare(self):
        os.environ['REQUEST_METHOD'] = 'GET'
        app.run()

        #self.assertEqual(sys.stdout.read(), DEFAULT_RESPONSE)

    def test_run_debug(self):
        debug = app.debug
        app.debug = True
        os.environ['REQUEST_METHOD'] = 'GET'
        os.environ['PATH_INFO'] = '/'

        res = app.run()
        #self.assertEqual(sys.stdout.read(), DEFAULT_RESPONSE)

        app.debug = debug

    '''
    def test_get_valid_methods(self):
        req = webtools.Request.blank('http://localhost:80/')
        req.app = app
        app.set_globals(app=app, request=req)

        handler = BrokenHandler(req, None)
        handler.app = app
        self.assertEqual(handler.get_valid_methods().sort(), ['GET'].sort())

        handler = HomeHandler(req, None)
        handler.app = app
        self.assertEqual(handler.get_valid_methods().sort(),
            ['GET', 'POST'].sort())

        handler = MethodsHandler(req, None)
        handler.app = app
        self.assertEqual(handler.get_valid_methods().sort(),
            ['GET', 'POST', 'HEAD', 'OPTIONS', 'PUT', 'DELETE', 'TRACE'].sort())
    '''

    def test_uri_for(self):
        class Handler(webtools.RequestHandler):
            def get(self, *args, **kwargs):
                pass

        req = webtools.Request.blank('http://localhost:80/')
        req.route = webtools.Route('')
        req.route_args = tuple()
        req.route_kwargs = {}
        req.app = app
        app.set_globals(app=app, request=req)
        handler = Handler(req, webtools.Response())
        handler.app = app

        for func in (handler.uri_for,):
            self.assertEqual(func('home'), '/')
            self.assertEqual(func('home', foo='bar'), '/?foo=bar')
            self.assertEqual(func('home', _fragment='my-anchor', foo='bar'), '/?foo=bar#my-anchor')
            self.assertEqual(func('home', _fragment='my-anchor'), '/#my-anchor')
            self.assertEqual(func('home', _full=True), 'http://localhost:80/')
            self.assertEqual(func('home', _full=True, _fragment='my-anchor'), 'http://localhost:80/#my-anchor')
            self.assertEqual(func('home', _scheme='https'), 'https://localhost:80/')
            self.assertEqual(func('home', _scheme='https', _full=False), 'https://localhost:80/')
            self.assertEqual(func('home', _scheme='https', _fragment='my-anchor'), 'https://localhost:80/#my-anchor')

            self.assertEqual(func('methods'), '/methods')
            self.assertEqual(func('methods', foo='bar'), '/methods?foo=bar')
            self.assertEqual(func('methods', _fragment='my-anchor', foo='bar'), '/methods?foo=bar#my-anchor')
            self.assertEqual(func('methods', _fragment='my-anchor'), '/methods#my-anchor')
            self.assertEqual(func('methods', _full=True), 'http://localhost:80/methods')
            self.assertEqual(func('methods', _full=True, _fragment='my-anchor'), 'http://localhost:80/methods#my-anchor')
            self.assertEqual(func('methods', _scheme='https'), 'https://localhost:80/methods')
            self.assertEqual(func('methods', _scheme='https', _full=False), 'https://localhost:80/methods')
            self.assertEqual(func('methods', _scheme='https', _fragment='my-anchor'), 'https://localhost:80/methods#my-anchor')

            self.assertEqual(func('route-test', year='2010', month='07', name='test'), '/2010/07/test')
            self.assertEqual(func('route-test', year='2010', month='07', name='test', foo='bar'), '/2010/07/test?foo=bar')
            self.assertEqual(func('route-test', _fragment='my-anchor', year='2010', month='07', name='test', foo='bar'), '/2010/07/test?foo=bar#my-anchor')
            self.assertEqual(func('route-test', _fragment='my-anchor', year='2010', month='07', name='test'), '/2010/07/test#my-anchor')
            self.assertEqual(func('route-test', _full=True, year='2010', month='07', name='test'), 'http://localhost:80/2010/07/test')
            self.assertEqual(func('route-test', _full=True, _fragment='my-anchor', year='2010', month='07', name='test'), 'http://localhost:80/2010/07/test#my-anchor')
            self.assertEqual(func('route-test', _scheme='https', year='2010', month='07', name='test'), 'https://localhost:80/2010/07/test')
            self.assertEqual(func('route-test', _scheme='https', _full=False, year='2010', month='07', name='test'), 'https://localhost:80/2010/07/test')
            self.assertEqual(func('route-test', _scheme='https', _fragment='my-anchor', year='2010', month='07', name='test'), 'https://localhost:80/2010/07/test#my-anchor')

    def test_extra_request_methods(self):
        allowed_methods_backup = app.allowed_methods
        webdav_methods = ('VERSION-CONTROL', 'UNLOCK', 'PROPFIND')

        for method in webdav_methods:
            # It is still not possible to use WebDav methods...
            req = webtools.Request.blank('/webdav')
            req.method = method
            rsp = req.get_response(app)
            self.assertEqual(rsp.status_int, 501)

        # Let's extend ALLOWED_METHODS with some WebDav methods.
        app.allowed_methods = tuple(app.allowed_methods) + webdav_methods

        #self.assertEqual(sorted(webtools.get_valid_methods(WebDavHandler)), sorted(list(webdav_methods)))

        # Now we can use WebDav methods...
        for method in webdav_methods:
            req = webtools.Request.blank('/webdav')
            req.method = method
            rsp = req.get_response(app)
            self.assertEqual(rsp.status_int, 200)
            self.assertEqual(rsp.text, 'Method: %s' % method)

        # Restore initial values.
        app.allowed_methods = allowed_methods_backup
        self.assertEqual(len(app.allowed_methods), 7)

    def test_escaping(self):
        def get_req(uri):
            req = webtools.Request.blank(uri)
            app.set_globals(app=app, request=req)
            handler = webtools.RequestHandler(req, None)
            handler.app = req.app = app
            return req, handler

        req, handler = get_req('http://localhost:80/')
        uri = webtools.uri_for('escape', name='with space')
        req, handler = get_req(uri)
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'with space')

        req, handler = get_req('http://localhost:80/')
        uri = webtools.uri_for('escape', name='with+plus')
        req, handler = get_req(uri)
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'with plus')

        req, handler = get_req('http://localhost:80/')
        uri = webtools.uri_for('escape', name='with/slash')
        req, handler = get_req(uri)
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'with/slash')

    def test_handle_exception_with_error(self):
        class HomeHandler(webtools.RequestHandler):
            def get(self, **kwargs):
                raise TypeError()

        def handle_exception(request, response, exception):
            raise ValueError()

        app = webtools.WSGIApplication([
            webtools.Route('/', HomeHandler, name='home'),
        ], debug=False)
        app.error_handlers[500] = handle_exception

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 500)

    def test_handle_exception_with_error_debug(self):
        class HomeHandler(webtools.RequestHandler):
            def get(self, **kwargs):
                raise TypeError()

        def handle_exception(request, response, exception):
            raise ValueError()

        app = webtools.WSGIApplication([
            webtools.Route('/', HomeHandler, name='home'),
        ], debug=True)
        app.error_handlers[500] = handle_exception

        req = webtools.Request.blank('/')
        self.assertRaises(ValueError, req.get_response, app)

    def test_function_handler(self):
        def my_view(request, *args, **kwargs):
            return webtools.Response('Hello, function world!')

        def other_view(request, *args, **kwargs):
            return webtools.Response('Hello again, function world!')

        '''
        def one_more_view(request, response):
            self.assertEqual(request.route_args, ())
            self.assertEqual(request.route_kwargs, {'foo': 'bar'})
            response.write('Hello you too, deprecated arguments world!')
        '''
        def one_more_view(request, *args, **kwargs):
            self.assertEqual(args, ())
            self.assertEqual(kwargs, {'foo': 'bar'})
            return webtools.Response('Hello you too!')

        app = webtools.WSGIApplication([
            webtools.Route('/', my_view),
            webtools.Route('/other', other_view),
            webtools.Route('/one-more/<foo>', one_more_view),
            #webtools.Route('/one-more/<foo>', one_more_view),
        ])

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello, function world!')

        # Twice to test factory.
        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello, function world!')

        req = webtools.Request.blank('/other')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello again, function world!')

        # Twice to test factory.
        req = webtools.Request.blank('/other')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello again, function world!')

        req = webtools.Request.blank('/one-more/bar')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello you too!')

    def test_custom_method(self):
        class MyHandler(webtools.RequestHandler):
            def my_method(self):
                self.response.write('Hello, custom method world!')

            def my_other_method(self):
                self.response.write('Hello again, custom method world!')

        app = webtools.WSGIApplication([
            webtools.Route('/', MyHandler, handler_method='my_method'),
            webtools.Route('/other', MyHandler, handler_method='my_other_method'),
        ])

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello, custom method world!')

        req = webtools.Request.blank('/other')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'Hello again, custom method world!')

    def test_custom_method_with_string(self):
        app = webtools.WSGIApplication([
            webtools.Route('/', handler='resources.handlers.CustomMethodHandler:custom_method'),
            webtools.Route('/bleh', handler='resources.handlers.CustomMethodHandler:custom_method'),
        ])

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'I am a custom method.')

        req = webtools.Request.blank('/bleh')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'I am a custom method.')

        self.assertRaises(ValueError, webtools.Route, '/', handler='resources.handlers.CustomMethodHandler:custom_method', handler_method='custom_method')

    def test_factory_1(self):
        app.debug = True
        rsp = app.get_response('/bare')
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'I am not a RequestHandler but I work.')
        app.debug = False

    def test_factory_2(self):
        """Very crazy stuff. Please ignore it."""
        class MyHandler(object):
            def __init__(self, request, response):
                self.request = request
                self.response = response

            def __new__(cls, *args, **kwargs):
                return cls.create_instance(*args, **kwargs)()

            @classmethod
            def create_instance(cls, *args, **kwargs):
                obj = object.__new__(cls)
                if isinstance(obj, cls):
                    obj.__init__(*args, **kwargs)

                return obj

            def __call__(self):
                return self

            def dispatch(self):
                self.response.write('hello')

        app = webtools.WSGIApplication([
            webtools.Route('/', handler=MyHandler),
        ])

        req = webtools.Request.blank('/')
        rsp = req.get_response(app)
        self.assertEqual(rsp.status_int, 200)
        self.assertEqual(rsp.text, 'hello')


if __name__ == '__main__':
    test_base.main()
