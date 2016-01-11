#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from pprint import pprint as pp
import sys

import pytest


def test_import():
    '''Basic test to determine if glfw can be imported successfully'''
    import glfw
    assert locals()['glfw'] == glfw


def test_pre_init():
    '''Tests functions from glfw core that can be run prior to running
    init (also including init)'''
    import glfw

    @glfw.decorators.error_callback
    def error_callback(error, description):
        pp('ERROR: {}: {}'.format(error, glfw._ffi.string(description)))

    # These can be called before init
    assert glfw.set_error_callback(error_callback) is None
    glfw_version = glfw.get_version()
    glfw_version_string = glfw.cdata_to_pystring(glfw.get_version_string())
    pp("GLFW Version String: {}".format(glfw_version_string))
    assert glfw_version is not None
    assert glfw_version_string.startswith(bytes('.'.join('{}'.format(v) for v in glfw_version).encode('utf-8')))
    assert glfw.init() != 0
    assert glfw.terminate() is None


def test_basic_package_functions():
    '''Runs tests on basic package information that is available to the
    end user
    '''
    import glfw
    assert glfw.get_include() is not None
    assert glfw.get_key_string(glfw.KEY_A) == 'a'
    assert glfw.get_mod_string(glfw.MOD_SHIFT) == 'shift'
    assert glfw.get_mouse_button_string(glfw.MOUSE_BUTTON_LEFT) == 'left'
    assert glfw.get_action_string(glfw.RELEASE) == 'release'


def test_basic_window():
    '''Runs a simple window example'''
    import glfw
    assert glfw.init() == glfw.gl.TRUE
    width, height = (1, 1)
    win = glfw.create_window(title='Simple window', width=width, height=height)
    for x in range(2):
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


def test_opengl_compatibility():
    import glfw
    from glfw import gl
    ffi = glfw._ffi
    assert glfw.init() == glfw.gl.TRUE
    opengl_version = None
    opengl_info = {}
    versions = [
        (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0),
        (3, 3), (3, 2), (3, 1), (3, 0),
        (2, 1), (2, 0),
        (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    ]
    farg = ffi.new('char []', bytes('OpenGL Compatibility'.encode('utf-8')))
    title = farg
    for major, minor in versions:
        version = major, minor
        try:
            # Request a specific version of opengl
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
            # Request a profile based on the version of opengl
            profile = glfw.OPENGL_ANY_PROFILE if version < (3, 2) else glfw.OPENGL_CORE_PROFILE
            glfw.window_hint(glfw.OPENGL_PROFILE, profile)
            # Setup forward compatibility if able
            forward_compat = False if version < (3, 0) else True
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, forward_compat)
            #  Keep the window invisible
            glfw.window_hint(glfw.VISIBLE, gl.GL_FALSE)
            # Generate a window anywhere on any monitor that's as small as possible
            window = glfw.core.create_window(1, 1, title, ffi.NULL, ffi.NULL)
            if window != ffi.NULL:
                glfw.make_context_current(window)
                # Save the highest version possible
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
                # Destroy every created window
                glfw.destroy_window(window)

        except Exception as e:
            for line in e.args:
                line = '{}'.format(line)
                print('ERROR: ' + line, file=sys.stderr)

    pp('OpenGL Version: {}'.format(opengl_info['version']))
    pp('OpenGL Vendor: {}'.format(opengl_info['vendor']))
    pp('OpenGL Renderer: {}'.format(opengl_info['renderer']))
    pp('OpenGL GLSL Supported: {}'.format(opengl_info['GLSL']))
    assert glfw.terminate() is None
    assert opengl_version in versions


if __name__ == '__main__':
    pytest.main()
