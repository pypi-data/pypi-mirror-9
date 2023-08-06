# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import types
import unittest

from . import call, parametrize, ParametrizedTestCase


class TestParametrizedTestCase(ParametrizedTestCase):
    @parametrize(
        call(1, 2, result=False),
        call(2, 2, result=True),
        positive=call(2, 2, result=True),
        negative=call(1, 2, result=False),
    )
    def test_method(self, given, expected, result):
        assert result == (given == expected), 'Invalid result'


class ParametrizedTestCaseTestCase(unittest.TestCase):
    def test_call_captures_and_returns_args_and_kwargs(self):
        result = call(1, 2, a=3)

        self.assertEqual(result, ((1, 2), {'a': 3}))

    def test_parametrize_attaches_params_to_object(self):
        @parametrize(
            call(1),
            named=call(2),
        )
        def test_func():
            pass

        self.assertTrue(hasattr(test_func, 'parameters'))
        self.assertEqual(test_func.parameters, (
            (call(1), ),
            {'named': call(2)},
        ))

    def test_template_method_is_removed(self):
        self.assertFalse(hasattr(TestParametrizedTestCase, 'test_method'))

    def test_cases_got_created(self):
        self.assertTrue(hasattr(TestParametrizedTestCase, 'test_method_case_1'))
        self.assertTrue(hasattr(TestParametrizedTestCase, 'test_method_case_2'))
        self.assertTrue(hasattr(TestParametrizedTestCase, 'test_method_positive'))
        self.assertTrue(hasattr(TestParametrizedTestCase, 'test_method_negative'))
