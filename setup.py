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
from setuptools import setup
import re

pattern = '^__(?P<key>[0-9_A-Za-z]+)__\s+\=\s+[\'"]?(?P<value>.*)[\'"]?$'
eng = re.compile(pattern)

top_folder = 'glfw'
# Grab information without importing
with open('{}/__init__.py'.format(top_folder), 'r') as fd:
    data = {}
    for line in fd:
        if eng.search(line):
            group_data = [m.groupdict() for m in eng.finditer(line)][0]
            key = group_data['key']
            value = group_data['value']
            if value.endswith("'"):
                value = value.rstrip("'")
            data[key] = value

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    with open('README.md', 'r') as fd:
        long_description = fd.read()


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
    packages=[top_folder],
    package_data={'': ['*.h']},
    classifiers=[
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Software Development :: User Interfaces',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy'
        ],
    install_requires=[
        'cffi', 'pyopengl', 'docopt', 'freetype-py', 'numpy'
    ]
)
