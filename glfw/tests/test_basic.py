#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from collections import namedtuple
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


def test_basic_window():
    import glfw
    assert glfw.init() not in [False, 0, None] or glfw.terminate()
    win = glfw.create_window()
    for x in range(2):
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


def test_opengl_compatibility():
    import glfw
    ffi = glfw._ffi
    gl = glfw.gl
    assert glfw.init() not in [False, 0, None] or glfw.terminate()
    opengl_version = None
    versions = [
        (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0),
        (3, 3), (3, 2), (3, 1), (3, 0),
        (2, 1), (2, 0),
        (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    ]
    farg = ffi.new('char []', bytes(''.encode('utf-8')))
    title = farg
    for major, minor in versions:
        try:
            glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
            glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
            glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
            glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
            glfw.window_hint(glfw.VISIBLE, gl.GL_FALSE)
            window = glfw.core.create_window(1, 1, title, ffi.NULL, ffi.NULL)
            if window != ffi.NULL:
                glfw.destroy_window(window)
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
    assert glfw.init() not in [False, 0, None] or glfw.terminate()
    gl = glfw.gl
    width, height = (640, 480)
    win = glfw.create_window(width=width, height=height)
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
    assert glfw.init() not in [False, 0, None] or glfw.terminate()
    gl = glfw.gl
    width, height = (640, 480)
    win = glfw.create_window(width=width, height=height)
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
    assert glfw.init() not in [False, 0, None] or glfw.terminate()
    win = glfw.create_window()
    for x in range(2):
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


if __name__ == '__main__':
    pytest.main()
