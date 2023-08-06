#!/usr/bin/env python

import os
import sys
from setuptools.command.test import test as TestCommand
import nekrobox

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        #import here, cause outside the
        #eggs aren't loaded
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)


readme = open('README.rst').read()

setup(
    name='nekrobox',
    version=nekrobox.__version__,
    description='A utilities library by Nekroze.',
    long_description=readme,
    author='Taylor "Nekroze" Lawson',
    author_email='tlawson@nekroze.com',
    url='https://lab.nekroze.com/tlawson/nekrobox',
    packages=[
        'nekrobox',
    ],
    package_dir={'nekrobox': 'nekrobox'},
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    keywords='nekrobox',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
    tests_require=['pytest>=2.3.5'],
    cmdclass = {'test': PyTest},
)
