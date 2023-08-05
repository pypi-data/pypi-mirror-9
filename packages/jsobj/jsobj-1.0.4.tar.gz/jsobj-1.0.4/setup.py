#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

if sys.version_info < (2, 6):
    raise NotImplementedError("Sorry, you need at least Python 2.6 or Python \
                               3.x to use jsobject.")

from setuptools.command.test import test as TestCommand


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


HERE = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(HERE, 'README.rst')).read()

if not os.path.exists('VERSION'):
    os.system("git describe --tags | cut -c 2- > VERSION")

version = open(os.path.join(HERE, 'VERSION')).read()[:-1]

#version = '1.0.0'

setup(
    name='jsobj',
    version=version,
    description='Jsobj provides JavaScript-Style Objects \
                 in Python.',
    long_description=readme,
    author='Geza Kovacs',
    author_email='geza0kovacs@gmail.com',
    url='https://github.com/gkovacs/jsobj',
    packages=find_packages(exclude=['ez_setup', 'tests', 'tests.*']),
    package_data={'jsobj': ['VERSION']},
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
    license='MIT',
    platforms='any',
    keywords=['jsobj', 'Object', 'json', 'chain', 'javascript'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
