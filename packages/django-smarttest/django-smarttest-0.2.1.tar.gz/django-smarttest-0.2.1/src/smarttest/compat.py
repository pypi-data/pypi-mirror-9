try:
    from django.test import override_settings
except ImportError:
    try:
        from django.test.utils import override_settings
    except ImportError:

        from django.conf import settings, UserSettingsHolder
        from django.utils.functional import wraps

        # Copied from django 1.3

        class override_settings(object):
            """
            Acts as either a decorator, or a context manager. If it's a decorator it
            takes a function and returns a wrapped function. If it's a contextmanager
            it's used with the ``with`` statement. In either event entering/exiting
            are called before and after, respectively, the function/block is executed.
            """
            def __init__(self, **kwargs):
                self.options = kwargs
                self.wrapped = settings._wrapped

            def __enter__(self):
                self.enable()

            def __exit__(self, exc_type, exc_value, traceback):
                self.disable()

            def __call__(self, test_func):
                from django.test import TransactionTestCase
                if isinstance(test_func, type) and issubclass(test_func, TransactionTestCase):
                    original_pre_setup = test_func._pre_setup
                    original_post_teardown = test_func._post_teardown

                    def _pre_setup(innerself):
                        self.enable()
                        original_pre_setup(innerself)

                    def _post_teardown(innerself):
                        original_post_teardown(innerself)
                        self.disable()
                    test_func._pre_setup = _pre_setup
                    test_func._post_teardown = _post_teardown
                    return test_func
                else:

                    @wraps(test_func)
                    def inner(*args, **kwargs):
                        with self:
                            return test_func(*args, **kwargs)
                return inner

            def enable(self):
                override = UserSettingsHolder(settings._wrapped)
                for key, new_value in self.options.items():
                    setattr(override, key, new_value)
                settings._wrapped = override

            def disable(self):
                settings._wrapped = self.wrapped


try:
    from django.test.client import RequestFactory
except ImportError:

    from StringIO import StringIO

    from django.http import SimpleCookie
    from django.core.handlers.wsgi import WSGIRequest
    from django.test.client import (
        encode_multipart, BOUNDARY, MULTIPART_CONTENT, CONTENT_TYPE_RE,
        smart_str, urllib, urlparse, urlencode, FakePayload)

    # Copied from django 1.3

    class RequestFactory(object):
        """
        Class that lets you create mock Request objects for use in testing.

        Usage:

        rf = RequestFactory()
        get_request = rf.get('/hello/')
        post_request = rf.post('/submit/', {'foo': 'bar'})

        Once you have a request object you can pass it to any view function,
        just as if that view had been hooked up using a URLconf.
        """
        def __init__(self, **defaults):
            self.defaults = defaults
            self.cookies = SimpleCookie()
            self.errors = StringIO()

        def _base_environ(self, **request):
            """
            The base environment for a request.
            """
            environ = {
                'HTTP_COOKIE': self.cookies.output(header='', sep='; '),
                'PATH_INFO': '/',
                'QUERY_STRING': '',
                'REMOTE_ADDR': '127.0.0.1',
                'REQUEST_METHOD': 'GET',
                'SCRIPT_NAME': '',
                'SERVER_NAME': 'testserver',
                'SERVER_PORT': '80',
                'SERVER_PROTOCOL': 'HTTP/1.1',
                'wsgi.version': (1, 0),
                'wsgi.url_scheme': 'http',
                'wsgi.errors': self.errors,
                'wsgi.multiprocess': True,
                'wsgi.multithread': False,
                'wsgi.run_once': False,
            }
            environ.update(self.defaults)
            environ.update(request)
            return environ

        def request(self, **request):
            "Construct a generic request object."
            return WSGIRequest(self._base_environ(**request))

        def _encode_data(self, data, content_type, ):
            if content_type is MULTIPART_CONTENT:
                return encode_multipart(BOUNDARY, data)
            else:
                # Encode the content so that the byte representation is correct.
                match = CONTENT_TYPE_RE.match(content_type)
                if match:
                    charset = match.group(1)
                else:
                    charset = settings.DEFAULT_CHARSET
                return smart_str(data, encoding=charset)

        def _get_path(self, parsed):
            # If there are parameters, add them
            if parsed[3]:
                return urllib.unquote(parsed[2] + ";" + parsed[3])
            else:
                return urllib.unquote(parsed[2])

        def get(self, path, data={}, **extra):
            "Construct a GET request"

            parsed = urlparse(path)
            r = {
                'CONTENT_TYPE': 'text/html; charset=utf-8',
                'PATH_INFO': self._get_path(parsed),
                'QUERY_STRING': urlencode(data, doseq=True) or parsed[4],
                'REQUEST_METHOD': 'GET',
                'wsgi.input': FakePayload('')
            }
            r.update(extra)
            return self.request(**r)

        def post(self, path, data={}, content_type=MULTIPART_CONTENT, **extra):
            "Construct a POST request."

            post_data = self._encode_data(data, content_type)

            parsed = urlparse(path)
            r = {
                'CONTENT_LENGTH': len(post_data),
                'CONTENT_TYPE': content_type,
                'PATH_INFO': self._get_path(parsed),
                'QUERY_STRING': parsed[4],
                'REQUEST_METHOD': 'POST',
                'wsgi.input': FakePayload(post_data),
            }
            r.update(extra)
            return self.request(**r)

        def head(self, path, data={}, **extra):
            "Construct a HEAD request."

            parsed = urlparse(path)
            r = {
                'CONTENT_TYPE': 'text/html; charset=utf-8',
                'PATH_INFO': self._get_path(parsed),
                'QUERY_STRING': urlencode(data, doseq=True) or parsed[4],
                'REQUEST_METHOD': 'HEAD',
                'wsgi.input': FakePayload('')
            }
            r.update(extra)
            return self.request(**r)

        def options(self, path, data={}, **extra):
            "Constrict an OPTIONS request"

            parsed = urlparse(path)
            r = {
                'PATH_INFO': self._get_path(parsed),
                'QUERY_STRING': urlencode(data, doseq=True) or parsed[4],
                'REQUEST_METHOD': 'OPTIONS',
                'wsgi.input': FakePayload('')
            }
            r.update(extra)
            return self.request(**r)

        def put(self, path, data={}, content_type=MULTIPART_CONTENT,
                **extra):
            "Construct a PUT request."

            put_data = self._encode_data(data, content_type)

            parsed = urlparse(path)
            r = {
                'CONTENT_LENGTH': len(put_data),
                'CONTENT_TYPE': content_type,
                'PATH_INFO': self._get_path(parsed),
                'QUERY_STRING': parsed[4],
                'REQUEST_METHOD': 'PUT',
                'wsgi.input': FakePayload(put_data),
            }
            r.update(extra)
            return self.request(**r)

        def delete(self, path, data={}, **extra):
            "Construct a DELETE request."

            parsed = urlparse(path)
            r = {
                'PATH_INFO': self._get_path(parsed),
                'QUERY_STRING': urlencode(data, doseq=True) or parsed[4],
                'REQUEST_METHOD': 'DELETE',
                'wsgi.input': FakePayload('')
            }
            r.update(extra)
            return self.request(**r)

__all__ = ['override_settings', 'RequestFactory']
