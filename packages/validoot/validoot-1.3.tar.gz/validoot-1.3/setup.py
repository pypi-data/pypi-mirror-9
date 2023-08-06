import os
import sys
from setuptools import setup
from setuptools.command.test import test

here = os.path.abspath(os.path.dirname(__file__))


class PyTest(test):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        test.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        test.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)

setup(
    # package info
    name='validoot',
    version='1.3',
    author='Ben Meier',
    author_email='benmeier@fastmail.com',
    url='http://github.com/AstromechZA/validoot',
    download_url='https://github.com/AstromechZA/validoot/tarball/1.3',
    description='Simple validation for function arguments using a decorator.',
    long_description=open(os.path.join(here, 'README.rst')).read(),
    keywords=[
        'validate',
        'function arguments',
        'decorator'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development'
    ],
    license='MIT',

    # packages
    packages=['validoot'],

    # runtime scripts
    scripts=[],

    # requirements
    install_requires=['wrapt'],

    # tests
    tests_require=['pytest-cov', 'pytest', 'mock'],
    cmdclass={'test': PyTest}
)
