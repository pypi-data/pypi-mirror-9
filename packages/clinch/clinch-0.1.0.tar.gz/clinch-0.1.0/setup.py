#!/usr/bin/env python3

import os.path
import sys

from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand

root = os.path.abspath(os.path.dirname(__file__))

def read_requirements(filename):
    path = os.path.join(root, filename)
    with open(path, 'rt') as f:
        return [line.strip() for line in f]

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
        exit_status = pytest.main(self.pytest_args)
        sys.exit(exit_status)

setup(
    name='clinch',
    version='0.1.0',
    packages=find_packages(),

    author='Eric Naeseth',
    author_email='eric@naeseth.com',

    tests_require=read_requirements('dev-requirements.txt'),
    cmdclass={'test': PyTest},

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
)
