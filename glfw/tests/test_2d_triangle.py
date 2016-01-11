from __future__ import print_function, division
from collections import namedtuple
import random

import pytest

Color3f = namedtuple('Color3f', ['r', 'g', 'b'])


def random_colors(count=1):
    colors = []
    for color in range(count):
        color = Color3f(random.random(), random.random(), random.random())
        colors.append(color)
    return colors


def test_basic_gl_snake_case_2d_triangle():
    import glfw
    assert glfw.init() == glfw.gl.TRUE
    gl = glfw.gl
    width, height = (1, 1)
    win = glfw.create_window(title='Snake case test', width=width, height=height)
    glfw.make_context_current(win)
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
    glfw.make_context_current(win)
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


if __name__ == '__main__':
    pytest.main()
