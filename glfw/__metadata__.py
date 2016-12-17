# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


__all__ = (
    '__project__', '__description__', '__versionstr__', '__author__',
    '__author_email__', '__maintainer__', '__maintainer_email__',
    '__copyright_years__', '__license__', '__url__', '__version__',
    '__classifiers__', '__keywords__', 'package_metadata',
)

# ----------------------------------------------------------------------
# Package Metadata
# ----------------------------------------------------------------------
__project__ = 'glfw-cffi'
__description__ = 'Foreign Function Interface wrapper for GLFW v3.x'
__license__ = 'Apache 2.0'
__versionstr__ = '0.3.0-dev'

__author__ = 'Brian Bruggeman'
__author_email__ = 'brian.m.bruggeman@gmail.com'

__maintainer__ = 'Brian Bruggeman'
__maintainer_email__ = 'brian.m.bruggeman@gmail.com'

__copyright_years__ = '2016'
__url__ = 'https://github.com/brianbruggeman/glfw-cffi.git'
__version__ = tuple([int(ver_i.split('-')[0]) for ver_i in __versionstr__.split('.')])

__classifiers__ = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Intended Audience :: Education',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Operating System :: POSIX',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: Implementation :: CPython',
    'Programming Language :: Python :: Implementation :: PyPy',
    'Programming Language :: Python',
    'Topic :: Multimedia :: Graphics :: 3D Rendering',
    'Topic :: Multimedia :: Graphics :: Viewers',
    'Topic :: Multimedia :: Graphics',
    'Topic :: Software Development :: User Interfaces',
]

__keywords__ = ['glfw', 'cffi', 'python', 'tool', 'utility']

# Package everything above into something nice and convenient for extracting
package_metadata = {k.strip('_'): v for k, v in locals().items() if k.startswith('__')}
