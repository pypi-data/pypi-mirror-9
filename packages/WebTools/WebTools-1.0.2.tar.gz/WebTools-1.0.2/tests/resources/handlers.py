import webtools


class LazyHandler(webtools.RequestHandler):
    def get(self, **kwargs):
        self.response.write('I am a laaazy view.')


class CustomMethodHandler(webtools.RequestHandler):
    def custom_method(self):
        self.response.write('I am a custom method.')


def handle_exception(request, response, exception):
    return webtools.Response(body='Hello, custom response world!')
