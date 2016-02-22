#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Wrapper file for Python GLFW CFFI library

Created by Brian Bruggeman
Copyright (c) 2016

License:  This file is released as Apache 2.0 license.  However, at
your option, you may apply any free software license you choose
provided that you adhere to the free software license chosen and
additionally follow these three criteria:
 a. list the author's name of this software as a contributor to your
    final product
 b. provide credit to your end user of your product or software without
    your end user asking for where you obtained your software
 c. notify the author of this software that you are using this software
 d. in addition, if you believe there can be some benefit in providing
    your changes upstream, you'll submit a change request.  While this
    criteria is completely optional, please consider not being a dick.
'''
import os
import re
import sys

from setuptools import setup
from setuptools.command.test import test as TestCommand

package_name = 'glfw'
# Grab package information without importing
with open('{}/__init__.py'.format(package_name), 'r') as fd:
    pattern = '^__(?P<key>[0-9_A-Za-z]+)__\s+\=\s+[\'"]?(?P<value>.*)[\'"]?$'
    eng = re.compile(pattern)
    data = {}
    for line in fd:
        if eng.search(line):
            group_data = [m.groupdict() for m in eng.finditer(line)][0]
            key = group_data['key']
            value = group_data['value']
            if value.endswith("'"):
                value = value.rstrip("'")
            data[key] = value

# Setup README documentation in RST format if pypandoc exists
try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    with open('README.md', 'r') as fd:
        long_description = fd.read()


# Setup tests
class PyTest(TestCommand):
    test_package_name = package_name

    def finalize_options(self):
        TestCommand.finalize_options(self)
        _test_args = [
            '--verbose',
            '--ignore=build',
            '--cov={0}'.format(self.test_package_name),
            '--cov-report=term-missing',
            '--pep8',
            '--flake8',
            '--norecursedirs'
            # error: error in setup.cfg: command 'PyTest' has no such option 'norecursedirs'
        ]
        extra_args = os.environ.get('PYTEST_EXTRA_ARGS')
        if extra_args is not None:
            _test_args.extend(extra_args.split())
        self.test_args = _test_args
        self.test_suite = True

    def run_tests(self):
        import pytest
        errno = pytest.main(self.test_args)
        sys.exit(errno)

install_requires = [
    'cffi',
    'pyopengl',
]

examples_require = [
    'docopt',
    'freetype-py',
    'numpy'
]

tests_require = [
    'pytest',
    'pytest-flake8',
    'pytest-cov',
    'pytest-xdist'
]


setup(
    name=data.get('title'),
    version=data.get('version'),
    author=data.get('author'),
    author_email=data.get('email'),
    description=data.get('shortdesc'),
    long_description=long_description,
    license=data.get('license'),
    url=data.get('url'),
    keywords='GLFW, CFFI',
    packages=[package_name],
    package_data={'': ['*.h']},
    classifiers=[
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Software Development :: User Interfaces',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: Apache Software License',
        'License :: Other/Proprietary License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
        ],
    install_requires=install_requires,
    extras_require={
        'examples': examples_require,
        'tests': tests_require,
    },
    setup_requires=['pytest-runner'],
    tests_require=tests_require,
    test_suite='{}.test'.format(package_name),
    cmdclass={'test': PyTest},
)
