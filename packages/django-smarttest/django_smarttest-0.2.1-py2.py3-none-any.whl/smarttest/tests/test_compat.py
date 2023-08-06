from django.conf import settings
from django.test import TestCase
from mock import sentinel

from smarttest.compat import override_settings, RequestFactory


class OverrideSettingsTest(TestCase):

    """
    :py:meth:`smarttest.compat.override_settings`
    """

    def test_should_override_debug(self):

        old_debug = settings.DEBUG
        new_debug = not old_debug
        with override_settings(DEBUG=new_debug):
            self.assertEqual(settings.DEBUG, new_debug)
        self.assertEqual(settings.DEBUG, old_debug)

    @override_settings(DEBUG=sentinel.debug)
    def test_should_override_debug_with_decorator(self):

        self.assertEqual(settings.DEBUG, sentinel.debug)


@override_settings(DEBUG=sentinel.debug)
class OverrideSettingsInClassTest(TestCase):

    """
    :py:meth:`smarttest.compat.override_settings`
    """

    def test_should_override_debug_with_decorator(self):

        self.assertEqual(settings.DEBUG, sentinel.debug)


class RequestFactoryGetTest(TestCase):

    """
    :py:meth:`smarttest.compat.RequestFactory.get`
    """

    def test_should_prepare_get_request(self):

        factory = RequestFactory()
        request = factory.get('/')
        self.assertEqual(request.method, 'GET')

    def test_should_prepare_get_request_with_params(self):

        factory = RequestFactory()
        request = factory.get('/abc;type=json')
        self.assertEqual(request.method, 'GET')


class RequestFactoryPostTest(TestCase):

    """
    :py:meth:`smarttest.compat.RequestFactory.post`
    """

    def test_should_prepare_post_request(self):

        factory = RequestFactory()
        request = factory.post('/')
        self.assertEqual(request.method, 'POST')

    def test_should_prepare_post_request_with_content_type(self):

        factory = RequestFactory()
        request = factory.post('/', content_type='application/json')
        self.assertEqual(request.method, 'POST')

    def test_should_prepare_post_request_with_content_type_and_encodint(self):

        factory = RequestFactory()
        request = factory.post('/', content_type='text/plain; charset=UTF-8')
        self.assertEqual(request.method, 'POST')


class RequestFactoryHeadTest(TestCase):

    """
    :py:meth:`smarttest.compat.RequestFactory.head`
    """

    def test_should_prepare_head_request(self):

        factory = RequestFactory()
        request = factory.head('/')
        self.assertEqual(request.method, 'HEAD')


class RequestFactoryOptionsTest(TestCase):

    """
    :py:meth:`smarttest.compat.RequestFactory.options`
    """

    def test_should_prepare_options_request(self):

        factory = RequestFactory()
        request = factory.options('/')
        self.assertEqual(request.method, 'OPTIONS')


class RequestFactoryPutTest(TestCase):

    """
    :py:meth:`smarttest.compat.RequestFactory.put`
    """

    def test_should_prepare_put_request(self):

        factory = RequestFactory()
        request = factory.put('/')
        self.assertEqual(request.method, 'PUT')


class RequestFactoryDeleteTest(TestCase):

    """
    :py:meth:`smarttest.compat.RequestFactory.delete`
    """

    def test_should_prepare_delete_request(self):

        factory = RequestFactory()
        request = factory.delete('/')
        self.assertEqual(request.method, 'DELETE')
