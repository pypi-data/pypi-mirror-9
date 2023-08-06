#!/usr/bin/env python3
import sys

from setuptools import setup
from setuptools import Command
# noinspection PyPep8Naming
from setuptools.command.test import test as TestCommand
exec(open('codeviking/random/_version.py').read())

from test.generate import generate_expected

class GenerateExpected(Command):
    """
    Generate Expected values for RNG, given several generators and seeds.
    """
    user_options=[]
    def run(self):
        generate_expected()
    def initialize_options(self):
        pass

    def finalize_options(self):
        pass



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
    name='CodeViking.random',
    version=__version__,
    url='https://bitbucket.org/codeviking/python-codeviking.random/',
    author='Dan Bullok',
    author_email='opensource@codeviking.com',
    description='Cross-language random number generators with many useful '
                'random number generation methods.',
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
    packages=['codeviking.random'],
    license="MIT",
    tests_require=['pytest', 'codeviking.math'],
    cmdclass={'test': PyTest,
              'generate_expected': GenerateExpected}
)
