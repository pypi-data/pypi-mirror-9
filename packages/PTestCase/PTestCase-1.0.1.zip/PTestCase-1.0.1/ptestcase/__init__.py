# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from unittest import TestCase
import six

__all__ = ['call', 'parametrize', 'ParametrizedTestCase']


try:
    # Try Python3 version, maybe someone will back-port this in the future?
    from functools import partialmethod
except ImportError:
    def partialmethod(func, *partial_args, **partial_kwargs):
        def new_method(self, *args, **kwargs):
            inner_kwargs = partial_kwargs.copy()
            inner_kwargs.update(kwargs)
            return func(self, *(partial_args + args), **inner_kwargs)

        return new_method


def call(*args, **kwargs):
    return args, kwargs


def parametrize(*unnamed_cases, **named_cases):
    def decorator(func):
        func.parameters = unnamed_cases, named_cases
        return func

    return decorator


class ParametrizedMeta(type):
    def __new__(mcs, name, bases, class_dict):
        for name in list(class_dict):  # Need a copy of keys, because we'll possibly be changing dict on the go
            attribute = class_dict[name]

            if hasattr(attribute, 'parameters'):
                # This is a parametrized method, create new versions and remove original one
                del class_dict[name]
                unnamed_cases, named_cases = attribute.parameters

                for i, (args, kwargs) in enumerate(unnamed_cases, start=1):
                    new_name = '{0}_case_{1:d}'.format(name, i)
                    class_dict[new_name] = partialmethod(attribute, *args, **kwargs)

                for case_name, (args, kwargs) in six.iteritems(named_cases):
                    new_name = '{0}_{1}'.format(name, case_name)
                    class_dict[new_name] = partialmethod(attribute, *args, **kwargs)

        return super(ParametrizedMeta, mcs).__new__(mcs, name, bases, class_dict)


class ParametrizedTestCase(six.with_metaclass(ParametrizedMeta, TestCase)):
    pass
