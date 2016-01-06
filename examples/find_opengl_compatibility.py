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
from OpenGL import GL as gl
import glfw


def get_opengl_compatibility(logger, ffi):
    if not glfw.init():
        glfw.terminate()
        raise RuntimeError('GLFW could not be initialized')
    logger.debug("Determining capabilities...")
    opengl_version = None
    versions = [
        (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0),
        (3, 3), (3, 2), (3, 1), (3, 0),
        (2, 1), (2, 0),
        (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    ]
    for major, minor in versions:
        try:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
            glfw.window_hint(glfw.VISIBLE, gl.GL_FALSE)
            window = glfw.create_window(width=1, height=1, title="NULL")
            if window != ffi.NULL:
                glfw.destroy_window(window)
                version = '.'.join('{}'.format(v) for v in (major, minor))
                logger.debug('Version "{}" is compatible.'.format(version))
                if opengl_version is None:
                    opengl_version = (major, minor)
        except Exception as e:
            import traceback as tb
            for line in tb.format_exc(e).split('\n'):
                logger.error(line)
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
    version = get_opengl_compatibility(logger, FFI())
    version = '.'.join('{}'.format(v) for v in version)
    logger.info('Version: {version}'.format(version=version))

    # Don't forget to make your graphics card happy.
    glfw.terminate()
