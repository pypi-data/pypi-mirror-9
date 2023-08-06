#########
Smarttest
#########

.. image:: https://pypip.in/wheel/django-smarttest/badge.svg
    :target: https://pypi.python.org/pypi/django-smarttest/
    :alt: Wheel Status

.. image:: https://pypip.in/version/django-smarttest/badge.svg
    :target: https://pypi.python.org/pypi/django-smarttest/
    :alt: Latest Version

.. image:: https://pypip.in/license/django-smarttest/badge.svg
    :target: https://pypi.python.org/pypi/django-smarttest/
    :alt: License


Goal
====

Provide code snippets which help running tests in Django.

Installation
============

Install requirements:

.. code-block:: console

    pip install -r requirements.txt

Install Smarttest:

.. code-block:: console

   pip install django-smarttest

or current development version:

.. code-block:: console

   pip install hg+https:://bitbucket.org/kidosoft/django-smarttest

Configuration
=============

.. code-block:: python

   INSTALLED_APPS =  [
    ...
    'smarttest',
    ...
   ]

Usage
=====

Preventing tests from touching database
---------------------------------------

.. code-block:: python

   import unittest

   from smarttest.decorators import no_db_testcase

   @no_db_testcase
   class SomeTestCase(unittest.TestCase):

        def test_some_test(self):
            ...

If you'll accidentally write code that tries to run some query on database
you'll get exception.

Running only selected test types
--------------------------------

.. code-block:: python

   import unittest

   from smarttest.decorators import test_type

   @test_type('acceptance')
   class SomeAcceptanceTestCase(unittest.TestCase):

        def test_some_acceptance_test(self):
            ...

   @test_type('unit')
   class SomeUnitTestCase(unittest.TestCase):

        def test_some_unit_test(self):
            ...

   class UnspecifiedTypeTestCase(unittest.TestCase):

        def test_some_test(self):
            ...

.. code-block:: python

   $ python -m unittest script
   ...
   ----------------------------------------------------------------------
   Ran 3 tests in 0.000s

   OK
   $ IGNORE_TESTS=unit python -m unittest script 
   .s.
   ----------------------------------------------------------------------
   Ran 3 tests in 0.000s

   OK (skipped=1)
   $ IGNORE_TESTS=acceptance python -m unittest script 
   s..
   ----------------------------------------------------------------------
   Ran 3 tests in 0.000s

   OK (skipped=1)
   $ IGNORE_TESTS=acceptance,unit python -m unittest script 
   ss.
   ----------------------------------------------------------------------
   Ran 3 tests in 0.000s

   OK (skipped=2)


Test type can be any selected word. It doesn't have to be "unit" or "acceptance". You can have different test types for running in different environments if you need.

TestCase for use with switchable splinter driver
------------------------------------------------

Simple TestCase that allows for simple switching between different drivers
in tests.

In settings.py:

.. code-block:: python

   TEST_DRIVER = 'firefox'  # or django or any other


In test:

.. code-block:: python

   from smarttest.testcases import SplinterTestCase

   class SomeTestCase(SplinterTestCase):

        def test_some_test(self):
            self.browser.visit(self.get_host() + '/')


If you run tests continuously (e.g. doing Test Driven Development)
TEST_DRIVER='django' (default setting) is the fastest driver that do not
interrupt your workflow. However when you run your acceptance tests you may want
to check how it behaves with real browser. Simply set TEST_DRIVER='firefox'
or any other real browser supported by splinter.


Supported Django versions
=========================

Tested with: 

* Django 1.2.7 on python2.7
* Django 1.3.7 on python2.7
* Django 1.4.16 on python2.7
* Django 1.5.11 on python2.7, python3.3, python3.4
* Django 1.6.8 on python2.7, python3.3, python3.4
* Django 1.7.1 on python2.7, python3.3, python3.4

Documentation
=============

http://kidosoft.pl/docs/django-smarttest/


