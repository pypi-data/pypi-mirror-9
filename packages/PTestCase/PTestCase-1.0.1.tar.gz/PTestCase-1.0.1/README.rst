.. image:: https://travis-ci.org/canni/ptestcase.svg?branch=master
    :target: https://travis-ci.org/canni/ptestcase

.. image:: https://coveralls.io/repos/canni/ptestcase/badge.png?branch=master
    :target: https://coveralls.io/r/canni/ptestcase?branch=master

PTestCase
=========

Isolated test cases generated from a template method and set of unnamed or named :term:`calls` provided
in decorator fashion.

Changelog
---------

- 1.0.1: Maintenance release, no BC breaks
- 1.0.0: Initial release

Installation
------------

Supports Python >= 2.6, Python 3 :sup:`*` and PyPy

``pip install ptestcase`` or ``easy_install ptestcase``

\* Although this works perfectly on Python 3, when yours code is targeting Python 3 **only**, you may use ``unittest``
module :term:`subtests` feature. If you need to support both Pythons from the same codebase, it's still the way to go.

The Problem:
------------

How to write test cases for this simple function without much boilerplate code?

.. code-block:: python

    def example(value, transform='lower'):
        if transform == 'lower:
            return value.lower()
        elif transform == 'upper':
            return value.upper()
        else:
            return value

Test cases using PTestCase:
---------------------------

Every ``call`` definition passed to ``parameterize`` will be converted to a test method, and original template will
be removed. Each generated test method will be executed in isolation, by the test runner.

.. code-block:: python

    from ptestcase import ParametrizedTestCase, call, parametrize

    class ExampleTestCase(ParametrizedTestCase):
        @parametrize(
            call('TEST', 'test', transform='lower'),
            call('test', 'TEST', transform='upper'),
            no_transform=call('test', 'test', None)
        )
        def test_template(self, given, expected, transform):
            result = example(given, transform)

            self.assertEqual(result, expected)

        def test_exception_on_invalid_value(self):
            with self.assertRises(AttributeError):
                example(None)

Example output:
---------------

.. code-block::

    running test
    test_template_case_1 (testpackage.ExampleTestCase) ... ok
    test_template_case_2 (testpackage.ExampleTestCase) ... ok
    test_template_no_transform (testpackage.ExampleTestCase) ... ok
    test_exception_on_invalid_input (testpackage.ExampleTestCase) ... ok
