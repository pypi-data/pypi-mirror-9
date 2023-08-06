# -*- coding: utf-8 -*-

from django.conf import settings
from django.test import TestCase
from splinter import Browser

TEST_DRIVER = getattr(settings, 'TEST_DRIVER', 'django')
try:
    from django.test import LiveServerTestCase
except ImportError:
    BaseTestCase = TestCase
else:
    BaseTestCase = LiveServerTestCase if TEST_DRIVER != 'django' else TestCase


class SplinterTestCase(BaseTestCase):

    def setUp(self):
        self.browser = Browser(TEST_DRIVER)

    def get_host(self):
        return getattr(self, 'live_server_url', '')
