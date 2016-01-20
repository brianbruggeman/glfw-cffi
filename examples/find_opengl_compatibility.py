#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Script to determine opengl compatibility

Usage:
    find_opengl_compatibility [options]

Options:
    -h --help        This message
    -v --verbose     Increases message output
'''
import sys

import OpenGL
OpenGL.ERROR_CHECKING = True
from OpenGL import GL as gl
import glfw

import sys


def get_opengl_compatibility(logger=None):
    ffi = glfw._ffi
    if logger is not None:
        logger.debug("Determining capabilities...")
    opengl_version = None
    opengl_info = {}
    versions = [
        (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0),
        (3, 3), (3, 2), (3, 1), (3, 0),
        (2, 1), (2, 0),
        (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    ]
    farg = ffi.new('char []', bytes(''.encode('utf-8')))
    title = farg

    if not glfw.core.init():
        glfw.terminate()
        raise RuntimeError('Could not initialize GLFW')

    for major, minor in versions:
        try:
            glfw.window_hint(glfw.FOCUSED, gl.GL_FALSE)
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
            glfw.window_hint(glfw.VISIBLE, gl.GL_FALSE)
            window = glfw.core.create_window(1, 1, title, ffi.NULL, ffi.NULL)
            if window != ffi.NULL:
                glfw.make_context_current(window)
                version = '.'.join('{}'.format(v) for v in (major, minor))
                if logger is not None:
                    logger.debug('Version "{}" is compatible.'.format(version))
                if opengl_version is None:
                    opengl_version = (major, minor)
                    opengl_info['version'] = gl.get_string(gl.VERSION)
                    opengl_info['vendor'] = gl.get_string(gl.VENDOR)
                    opengl_info['renderer'] = gl.get_string(gl.RENDERER)
                    opengl_info['GLSL'] = gl.get_string(gl.SHADING_LANGUAGE_VERSION)

                    # Display Extension information
                    if version < (3, 1):
                        extension_count = gl.glGetIntegerv(gl.EXTENSIONS)
                        for index in range(extension_count):
                            extension_string = gl.get_string(gl.EXTENSIONS, index)
                            opengl_info.setdefault('extensions', []).append(extension_string)

                    # Display GLSL Versions
                    if version >= (4, 3):
                        glsl_version_count = gl.glGetIntegerv(gl.NUM_SHADING_LANGUAGE_VERSIONS)
                        for index in range(glsl_version_count):
                            glsl_version = gl.get_string(gl.SHADING_LANGUAGE_VERSION, index)
                            opengl_info.setdefault('glsl_supported', []).append(glsl_version)
                glfw.destroy_window(window)

        except Exception as e:
            for line in e.args:
                line = '{}'.format(line)
                print('ERROR: ' + line, file=sys.stderr)

    glfw.terminate()
    return opengl_version


if __name__ == '__main__':
    import logging

    from cffi import FFI
    from docopt import docopt

    def fix(option):
        '''Formats docopt eccentricities into something compatible to send
        into a python function.

        >>> def example_function(verbose=False, **options):
        ...     pass
        >>> options = docopt(__doc__)
        >>> example_function(**options)  # Causes an exception
        >>> options = {fix(k): v for k, v in docopt(__doc__).items()}
        >>> example_function(**options)  # No exception
        '''
        option = option.lstrip('-')
        option = option.lstrip('<').rstrip('>')
        option = option.replace('-', '_')
        return option

    # Capture command-line options
    options = {fix(k): v for k, v in docopt(__doc__).items()}

    # setup logging
    if options.get('verbose'):
        logging.basicConfig(level=logging.DEBUG)
    elif options.get('quiet'):
        logging.basicConfig(level=logging.WARNING)
    else:
        logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger('OpenGL Compatibility')

    # determine version and display
    version = get_opengl_compatibility(logger)
    version = '.'.join('{}'.format(v) for v in version)
    logger.info('Version: {version}'.format(version=version))
