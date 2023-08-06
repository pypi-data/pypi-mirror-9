""" Decorators that help with running tests. """

__doc__ = """
Decorators
==========
"""

import os
import unittest

import mock


def no_db_testcase(func):
    """ Decorator that prevents your test touching database.

    :raises RuntimeError: if test try to do database query
    """
    exception = RuntimeError("Do not touch the database!")
    cursor_wrapper = mock.MagicMock(side_effect=exception)
    mocking_dict = {
        'execute': cursor_wrapper,
        'executemany': cursor_wrapper,
        'callproc': cursor_wrapper,
    }
    try:
        from django.db.backends.util import CursorWrapper
    except ImportError:
        # Django < 1.3 has no CursorWrapper so give support at least for sqlite
        from django.db.backends.sqlite3.base import SQLiteCursorWrapper as CursorWrapper
        del mocking_dict['callproc']
    try:
        CursorWrapper.execute
    except AttributeError:
        # Django < 1.6 uses __getattr__
        mocking_dict = {'__getattr__': cursor_wrapper}
    wrapped = mock.patch.multiple(CursorWrapper, **mocking_dict)
    return wrapped(func)


def test_type(name):
    """ Function creating decorators that allows skipping tests of declared type.

    :param str name: arbitrary name of test type e.g. acceptance,unit
    """
    should_ignore = (name in os.environ.get('IGNORE_TESTS', ''))
    return unittest.skipIf(should_ignore, '%s test skipped' % name)
