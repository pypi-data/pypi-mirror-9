import os
import unittest

from django.test import TestCase
from smarttest.decorators import no_db_testcase, test_type


class NoDbTestCaseTest(TestCase):

    """
    :py:meth:`smarttest.decorators.no_db_testcase`
    """

    def test_should_raise_exception_on_cursor_db_access(self):

        @no_db_testcase
        def decorated_func(*args, **kwargs):
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute('select 1;')

        self.assertRaises(RuntimeError, decorated_func)

    def test_should_raise_exception_on_orm_db_access(self):

        @no_db_testcase
        def decorated_func(*args, **kwargs):
            from django.contrib.auth.models import User
            User.objects.count()

        self.assertRaises(RuntimeError, decorated_func)


class TestTypeTest(TestCase):

    """
    :py:meth:`smarttest.decorators.test_type`
    """

    def test_should_skip_test(self):

        os.environ['IGNORE_TESTS'] = 'acceptance'

        def func():
            pass  # pragma: no coverage

        decorator = test_type('acceptance')
        decorated_func = decorator(func)

        self.assertRaises(unittest.SkipTest, decorated_func)

    def test_should_run_test(self):

        os.environ['IGNORE_TESTS'] = 'unit'

        def func():
            pass  # pragma: no coverage

        decorator = test_type('acceptance')
        decorated_func = decorator(func)

        try:
            decorated_func()
        except unittest.SkipTest:  # pragma: no coverage
            self.fail('Should not skip test')  # pragma: no coverage
