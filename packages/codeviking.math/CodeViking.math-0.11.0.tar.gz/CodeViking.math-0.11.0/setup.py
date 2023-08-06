#!/usr/bin/env python3
import sys

from setuptools import setup
# noinspection PyPep8Naming
from setuptools.command.test import test as TestCommand

exec(open('codeviking/math/_version.py').read())

class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest

        errno = pytest.main(self.test_args)
        sys.exit(errno)


LONG_DESCRIPTION = open('README.rst').read()

setup(
    name='CodeViking.math',
    version=__version__,
    url='https://bitbucket.org/codeviking/python-codeviking.math/',
    author='Dan Bullok',
    author_email='opensource@codeviking.com',
    description='Function and method call math',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Quality Assurance'
    ],
    platforms='any',
    namespace_packages=['codeviking'],
    packages=['codeviking.math'],
    license="MIT",
    tests_require=['pytest'],
    cmdclass={'test': PyTest}
)
