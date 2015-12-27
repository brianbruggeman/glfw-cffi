#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ######################################################################
#  Wrapper file for Python GLFW CFFI library
#  Used GLFW v3.2 api
#  Created by Brian Bruggeman
#  Copyright (c) 2016
#
#  License:  This file is released as Apache 2.0 license.  However, at
#  your option, you may apply any free software license you choose
#  provided that you adhere to the free software license chosen and
#  additionally follow these three criteria:
#   a. list the author's name of this software as a contributor to your
#      final product
#   b. provide credit to your end user of your product or software without
#      your end user asking for where you obtained your software
#   c. notify the author of this software that you are using this software
#   d. in addition, if you believe there can be some benefit in providing
#      your changes upstream, you'll submit a change request.  While this
#      criteria is completely optional, please consider not being a dick.
# ######################################################################
from setuptools import setup


setup(
    name='glfw-cffi',
    version='0.1.0',
    author='Brian Bruggeman',
    author_email='brian.m.bruggeman@gmail.com',
    description='Foreign Function Interface wrapper for GLFW v3.x',
    license='Apache 2.0',
    url='https://github.com/brianbruggeman/glfw-cffi.git',
    keywords='GLFW, CFFI',
    packages=['glfw'],
    package_data={'glfw': ['glfw/*.h']},
    classifiers=[
        'Topic :: Multimedia :: Graphics',
        'Topic :: Multimedia :: Graphics :: 3D Rendering',
        'Topic :: Multimedia :: Graphics :: Viewers',
        'Topic :: Software Development :: User Interfaces',
        'Intended Audience :: Education',
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: PyPy'
        ],
    requires=['cffi']
)
