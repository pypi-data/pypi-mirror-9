#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open("garland.py", "r") as module_file:
    for line in module_file:
        if line.startswith("__version__"):
            version_string = line.split("=")[1]
            version = version_string.strip().replace("'", "")


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
    version=version,
    description='Python decorator mocking.',
    long_description=readme + '\n\n' + history,
    author='Ben Lopatin',
    author_email='ben@wellfire.co',
    url='https://github.com/bennylope/garland',
    py_modules=['garland'],
    include_package_data=True,
    license="BSD",
    zip_safe=False,
    keywords='garland',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
