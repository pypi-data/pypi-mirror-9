# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import ez_setup
ez_setup.use_setuptools()

from setuptools import setup, find_packages

setup(
    name='PTestCase',
    description='Parametrized tests support for python builtin unitest framework',
    long_description=(
        'Isolated test cases generated from a template method and set of unnamed or named :term:`calls` '
        'provided in decorator fashion.'
    ),
    version='1.0.1',
    packages=find_packages(),
    author='Dariusz Górecki',
    author_email='darek.krk@gmail.com',
    url='https://github.com/canni/ptestcase',
    keywords=['test', 'parametrized', 'unittest'],
    install_requires=[
        'six',
    ],
    zip_safe=True,
    test_suite='ptestcase.tests',
    license='BSD License',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    platforms=['any'],
)
