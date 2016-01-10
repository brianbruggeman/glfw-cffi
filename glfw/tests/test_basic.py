#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from collections import namedtuple
from pprint import pprint as pp
import sys
import random

import pytest

Color3f = namedtuple('Color3f', ['r', 'g', 'b'])


def random_colors(count=1):
    colors = []
    for color in range(count):
        color = Color3f(random.random(), random.random(), random.random())
        colors.append(color)
    return colors


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
        pp('{}: {}'.format(error, description))

    # These can be called before init
    assert glfw.set_error_callback(error_callback) is None
    version = glfw.get_version()
    version_string = glfw.cdata_to_pystring(glfw.get_version_string())
    pp("GLFW Version String: {}".format(version_string))
    assert version is not None
    assert version_string.startswith(bytes('.'.join('{}'.format(v) for v in version).encode('utf-8')))
    assert glfw.init() != 0
    assert glfw.terminate() is None


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
    ffi = glfw._ffi
    gl = glfw.gl
    assert glfw.init() == glfw.gl.TRUE
    opengl_version = None
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
                # Destroy every created window
                glfw.destroy_window(window)
                # Save the highest version possible
                if opengl_version is None:
                    opengl_version = (major, minor)
        except Exception as e:
            import traceback as tb
            for line in tb.format_exc(e).split('\n'):
                print(line, file=sys.stderr)
    assert glfw.terminate() is None
    assert opengl_version in versions


def test_basic_gl_snake_case_2d_triangle():
    import glfw
    assert glfw.init() == glfw.gl.TRUE
    gl = glfw.gl
    width, height = (1, 1)
    win = glfw.create_window(title='Snake case test', width=width, height=height)
    gl.enable(gl.DEPTH_TEST)
    gl.depth_func(gl.LESS)
    gl.clear_color(0, 0, 0, 0)
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
    for x in range(2):
        gl.begin(gl.TRIANGLES)
        colors = random_colors(3)
        gl.color_3f(*colors[0])
        gl.vertex_3f(0, 0, 0)
        gl.color_3f(*colors[1])
        gl.vertex_3f(width, 0, 0)
        gl.color_3f(*colors[2])
        gl.vertex_3f(0, height, 0)
        gl.end()
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


def test_basic_gl_camelCase_2d_triangle():
    import glfw
    assert glfw.init() == glfw.gl.TRUE
    gl = glfw.gl
    width, height = (1, 1)
    win = glfw.create_window(title='CamelCase test', width=width, height=height)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)
    gl.glClearColor(0, 0, 0, 0)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    for x in range(2):
        gl.glBegin(gl.GL_TRIANGLES)
        colors = random_colors(3)
        gl.glColor3f(*colors[0])
        gl.glVertex3f(0, 0, 0)
        gl.glColor3f(*colors[1])
        gl.glVertex3f(width, 0, 0)
        gl.glColor3f(*colors[2])
        gl.glVertex3f(0, height, 0)
        gl.glEnd()
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


def test_basic_gl_vbo_triangle():
    import glfw
    assert glfw.init() == glfw.gl.TRUE
    width, height = (1, 1)
    win = glfw.create_window(title='Shader test', width=width, height=height)
    for x in range(2):
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


if __name__ == '__main__':
    pytest.main()
