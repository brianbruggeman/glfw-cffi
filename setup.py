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
from __future__ import absolute_import, division, print_function, unicode_literals

import datetime
import os
import re

from setuptools import find_packages, setup


def setup_project():
    '''Sets up project as needed.

    This function should be manually updated as needed.  Placed at the
    top of the file for better grokking.

    When developing, simply run (from within a virtualenv):

        $ pip install .[all]

    Returns:
        package_requires(list): List of required packages
        links(list): list of private package links
        classifiers(list): standard python package classifiers
    '''
    # Whatever dependencies package requires
    package_requires = [
        'cffi',
        'pyopengl',
    ]

    private_packages = []
    package_requires += private_packages

    # Links if needed for private repos
    links = []

    # Project classifiers
    classifiers = [
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

    return package_requires, links, classifiers


# ----------------------------------------------------------------------
# Generally, only edit above this line
# ----------------------------------------------------------------------
def get_package_metadata(project_name=None):
    '''Captures metadata information for package

    Providing the project name will reduce the search/install time.

    Args:
        project_name: top project folder and project name

    Returns:
        dict: package metdata
    '''
    top_folder = os.path.abspath(os.path.dirname(__file__))
    required_fields = ['version', 'license', 'url', 'description', 'project']
    metadata = {}
    missing_message = []
    package_names = [p for p in find_packages() if '.' not in p]
    for root, folder, files in os.walk(top_folder):
        if not any(root.endswith(p) for p in package_names):
            continue
        for filename in files:
            if filename == '__metadata__.py':
                filepath = os.path.join(root, filename)
                relpath = filepath.replace(top_folder, '').lstrip('/')
                with open(os.path.join(filepath)) as fd:
                    exec(fd.read(), metadata)
                if 'package_metadata' in metadata:
                    metadata = metadata.get('package_metadata', {})
                if not all(field in metadata for field in required_fields):
                    missing = ', '.join(
                        field
                        for field in sorted(required_fields)
                        if field not in metadata
                    )
                    missing_message.append('{} is missing: {}'.format(relpath, missing))
                    metadata = {}
            if metadata:
                break
        if metadata:
            break
    if not metadata:
        print('Required package fields: {}'.format(', '.join(sorted(required_fields))))
        print('\n'.join(missing_message))
        raise Exception('Could not find package')
    if 'doc' not in metadata:
        if os.path.exists('README.md'):
            try:
                import pypandoc
                metadata['doc'] = pypandoc.convert('README.md', 'rst')
            except ImportError:
                with open('README.md', 'r') as fd:
                    metadata['doc'] = fd.read()
        elif os.path.exists('README.rst'):
            with open('README.rst', 'r') as fd:
                metadata['doc'] = fd.read()
    return metadata


def get_package_requirements(package_requires, required=None):
    '''Convenience function to wrap package_requires

    Args:
        required(list): list of required packages to run
    Returns:
        dict: A better format of requirements
    '''
    required = package_requires if not required else required
    requirements = {
        # Debug probably is only necessary for development environments
        'debug': [
            'ipython',
            'pdbpp',
        ],

        # Docs should probably only be necessary in Continuous Integration
        'docs': [
            'coverage',
            'pandoc',
            'sphinx',
            'sphinx_rtd_theme',
            'sphinxcontrib-napoleon',
        ],

        # Examples probably is only necessary for development environments
        'examples': [
            'docopt',
            'freetype-py',
            'numpy',
            'pyyaml',
        ],

        # Requirements is the basic needs for this package
        'requirements': required,

        # Required for installation
        'setup': [
            'pip',
            'pytest-runner',
        ],

        # Required for running scripts
        'scripts': [
            'GitPython',
            'docopt',
        ],

        # Tests are needed in a local and CI environments for py.test and tox
        # Note:  To run the tox environment for docs, docs must also be installed
        'tests': [
            'detox',
            'flask-debugtoolbar',
            'numpy',
            'pdbpp',
            'pytest',
            'pytest-cov',
            'pytest-flake8',
            'pytest-html',
            'pytest-xdist',
            'tox',
        ],

    }

    # Developers should probably run:  pip install .[dev]
    requirements['dev'] = [
        r for k, reqs in requirements.items() for r in reqs
        if k not in ['requirements']
    ]

    # All is for usability:  pip install .[all]
    requirements['all'] = [
        r for k, reqs in requirements.items() for r in reqs
    ]

    return requirements


def get_console_scripts(metadata):
    '''Convenience function to wrap console scripts.

    Expects that all command-line scripts are found within the
    __main__.py file and that they are functions.

    Args:
        metadata(dict): project metadata

    Returns:
        list: scripts listed in format required by setup
    '''
    scripts = []
    project_name = metadata['project']
    project_folder = os.path.abspath(os.path.dirname(__file__))
    filepath = '{project_folder}/{project_name}/__main__.py'
    filepath = filepath.format(project_folder=project_folder, project_name=project_name)
    engine = re.compile(r"^def (?P<func>(.*?))\((?P<args>(.*?))\)\:$")
    template = '{script} = {project_name}.__main__:{func_name}'
    if os.path.exists(filepath):
        with open(filepath, 'r') as fd:
            for line in fd:
                for data in [m.groupdict() for m in engine.finditer(line)]:
                    func_name = data['func']
                    script = func_name.replace('_', '-')
                    scripts.append(template.format(script=script, project_name=project_name, func_name=func_name))
    return scripts


def main():
    '''Sets up the package'''
    metadata = get_package_metadata()
    package_requires, links, classifiers = setup_project()
    requirements = get_package_requirements(package_requires=package_requires)
    project_name = metadata['project']
    extras = {k: v for k, v in requirements.items() if k != 'requirements'}
    year = metadata.get('copyright_years') or datetime.datetime.now().year
    lic = metadata.get('license') or 'Copyright {year} - all rights reserved'.format(year=year)

    # Run setup
    setup(
        # Package metadata information
        name=project_name,
        version=metadata.get('version_str') or 'unknown',
        description=metadata.get('shortdoc') or project_name,
        long_description=metadata.get('doc') or metadata.get('shortdoc') or project_name,
        url=metadata.get('url') or '',
        license=lic,
        author=metadata.get('author') or 'unknown',
        author_email=metadata.get('email') or 'unknown',
        keywords='GLFW, CFFI',

        # Package Properties
        packages=find_packages(),
        include_package_data=True,

        # Requirements
        setup_requires=requirements.get('setup') or [],
        install_requires=requirements['requirements'],
        extras_require=extras,
        tests_require=requirements.get('tests') or [],
        dependency_links=links,
        entry_points={
            'console_scripts': get_console_scripts(metadata),
        },
        platforms=['any'],
        classifiers=classifiers,
        zip_safe=False,
    )


if __name__ == '__main__':
    main()
