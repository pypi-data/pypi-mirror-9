#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    os.system('python setup.py bdist_wheel upload')
    sys.exit()


readme = open('README.rst').read()
history = open('HISTORY.rst').read().replace('.. :changelog:', '')

test_requirements = [
    'mock',  # For older Python versions
]

setup(
    name='garland',
    version='0.1.0',
    description='Python decorator mocking.',
    long_description=readme + '\n\n' + history,
    author='Ben Lopatin',
    author_email='ben@wellfire.co',
    url='https://github.com/bennylope/garland',
    py_modules=['garland'],
    #packages=[
    #    'garland',
    #],
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords='garland',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
