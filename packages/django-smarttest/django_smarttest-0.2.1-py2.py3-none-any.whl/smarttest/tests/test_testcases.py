from unittest import skipIf

from django.test import TestCase
try:
    from django.test import LiveServerTestCase  # noqa
except ImportError:
    NO_LIVE_SERVER = True
else:
    NO_LIVE_SERVER = False

from mock import Mock, patch
from six.moves import reload_module

from smarttest.compat import override_settings
import smarttest.testcases


class SplinterTestCaseGetHostTestCase(TestCase):

    """
    :py:meth:`SplinterTestCase.get_host`.
    """

    @skipIf(NO_LIVE_SERVER, 'No LiveServerTestCase in older Django')
    def test_should_return_live_server_url_on_firefox_driver(self):
        with override_settings(TEST_DRIVER='firefox'):
            reload_module(smarttest.testcases)

            smarttest.testcases.SplinterTestCase.runTest = Mock()
            obj = smarttest.testcases.SplinterTestCase()
            host = 'localhost'
            port = '8081'
            obj.server_thread = Mock(host=host, port=port)
            result = obj.get_host()
            self.assertEqual(result, 'http://%s:%s' % (host, port))

    def test_should_return_empty_url_on_django_driver(self):
        with override_settings(TEST_DRIVER='django'):
            reload_module(smarttest.testcases)

            smarttest.testcases.SplinterTestCase.runTest = Mock()
            obj = smarttest.testcases.SplinterTestCase()
            result = obj.get_host()
            self.assertEqual(result, '')


class SplinterTestCaseSetUpTestCase(TestCase):

    """
    :py:meth:`SplinterTestCase.setUp`
    """

    @patch('smarttest.testcases.Browser')
    def test_should_create_browser(self, Browser):
        smarttest.testcases.SplinterTestCase.runTest = Mock()
        obj = smarttest.testcases.SplinterTestCase()
        obj.setUp()
        self.assertTrue(getattr(obj, 'browser', None))
        self.assertTrue(Browser.called)
