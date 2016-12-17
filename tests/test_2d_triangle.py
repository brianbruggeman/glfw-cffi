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


@pytest.mark.unit
def test_basic_gl_snake_case_2d_triangle(windowed_fullscreen):
    import glfw
    from glfw import gl
    assert glfw.init() == glfw.gl.TRUE

    win = windowed_fullscreen
    width, height = glfw.get_window_size(win)
    assert win != glfw.ffi.NULL
    gl.enable(gl.DEPTH_TEST)
    gl.depth_func(gl.LESS)
    gl.clear_color(0, 0, 0, 0)
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
    for x in range(10):
        gl.begin(gl.TRIANGLES)
        colors = random_colors(3)
        gl.color_3f(*colors[0])
        gl.vertex_3f(0, 0, 0)
        gl.color_3f(*colors[1])
        gl.vertex_3f(width, 0, 0)
        gl.color_3f(*colors[2])
        gl.vertex_3f(0, height, 0)
        # gl.end()
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


@pytest.mark.unit
def test_basic_gl_camelCase_2d_triangle(windowed_fullscreen):
    import glfw
    from glfw import gl
    assert glfw.init() == glfw.gl.TRUE

    win = windowed_fullscreen
    width, height = glfw.get_window_size(win)
    assert win != glfw.ffi.NULL
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
        # gl.glEnd()
        assert glfw.swap_buffers(win) is None
        assert glfw.poll_events() is None
    assert win is not None
    assert glfw.terminate() is None


@pytest.mark.unit
def test_shaders_2d_triangle(window):
    from textwrap import dedent as dd
    import ctypes
    from random import random as rand

    import numpy as np
    import glfw
    from glfw import gl

    vshader = '''
    #version 410

    in vec2 position;
    in vec3 color;

    out vec3 v_color;


    void main () {
        gl_Position = vec4(position, 0.0, 1.0);
        v_color = color;
    }
    '''
    fshader = '''
    #version 410

    in vec3 v_color;

    out vec4 frag_colour;

    void main () {
        frag_colour = vec4(v_color, 1.0);
    }
    '''
    pt = 0.5
    vertices = np.array([
        (x, y) for x in [-pt, 0, pt] for y in [-pt, 0, pt]
    ], dtype=np.float32)

    indices = np.array([
        # index for index in range(vertices.shape[0])
        5, 6, 0,
    ], dtype=np.uint32)

    rgb = 3
    colors = np.array([
        [rand() for _ in range(rgb)]  # vec3 of colors
        for v in vertices  # one for every index
    ], dtype=np.float32)

    data = np.zeros(
        len(vertices),
        dtype=[
            ('position', np.float32, vertices.shape[-1]),
            ('color', np.float32, colors.shape[-1]),
        ]
    )

    # Interleave vertex data for position and color
    data['position'] = vertices
    data['color'] = colors

    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glDepthFunc(gl.GL_LESS)

    # Build pipeline
    program = gl.glCreateProgram()
    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, dd(vshader))
    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

    gl.glShaderSource(fragment_shader, dd(fshader))
    gl.glCompileShader(vertex_shader)
    gl.glCompileShader(fragment_shader)

    # v_result = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
    v_log = gl.glGetShaderiv(vertex_shader, gl.GL_INFO_LOG_LENGTH)
    if v_log > 0:
        v_error_message = gl.glGetShaderInfoLog(vertex_shader)
        error_message = v_error_message.split(':')[-1].strip()
        print('ERROR: Vertex Shader Compilation | {}'.format(error_message))

    # f_result = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
    f_log = gl.glGetShaderiv(fragment_shader, gl.GL_INFO_LOG_LENGTH)
    if f_log > 0:
        f_error_message = gl.glGetShaderInfoLog(fragment_shader)
        error_message = f_error_message.split(':')[-1].strip()
        print('ERROR: Fragment Shader Compilation | {}'.format(error_message))

    # Link Shaders to Program
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)

    # p_result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
    p_log = gl.glGetProgramiv(program, gl.GL_INFO_LOG_LENGTH)
    if p_log > 0:
        p_error_message = gl.glGetProgramInfoLog(program)
        error_message = p_error_message.split(':')[-1].strip()
        print('ERROR: Program Linking | {}'.format(error_message))

    # Cleanup shaders
    gl.glDetachShader(program, vertex_shader)
    gl.glDetachShader(program, fragment_shader)

    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)

    gl.glBindAttribLocation(program, 0, 'position')
    gl.glBindAttribLocation(program, 1, 'color')

    gl.glClearColor(0.1, 0.1, 0.1, 1.0)

    vao = gl.glGenVertexArrays(1)
    buffer_id = gl.glGenBuffers(1)
    indices_buffer_id = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer_id)

    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.flatten(), gl.GL_STATIC_DRAW)

    for x in range(2):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glPolygonMode(gl.GL_FRONT_AND_BACK, gl.GL_LINE)
        gl.glEnable(gl.DEPTH_TEST)
        gl.glDepthFunc(gl.LESS)
        gl.glUseProgram(program)
        gl.glBufferData(gl.GL_ARRAY_BUFFER, data.nbytes, data, gl.GL_DYNAMIC_DRAW)

        gl.glBindVertexArray(vao)
        stride = data.strides[0]

        offset = ctypes.c_void_p(0)
        pos = gl.glGetAttribLocation(program, 'position')
        gl.glEnableVertexAttribArray(pos)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer_id)
        gl.glVertexAttribPointer(pos, data['position'].shape[-1], gl.GL_FLOAT, False, stride, offset)

        offset = ctypes.c_void_p(data.dtype['position'].itemsize)
        col = gl.glGetAttribLocation(program, 'color')
        gl.glEnableVertexAttribArray(col)
        gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer_id)
        gl.glVertexAttribPointer(col, data['color'].shape[-1], gl.GL_FLOAT, False, stride, offset)

        gl.glDrawElements(gl.TRIANGLES, len(indices), gl.GL_UNSIGNED_INT, None)

        # Cleanup
        gl.glDisableVertexAttribArray(vao)
        # Standard Loop Event handling
        glfw.core.swap_buffers(window)
        glfw.core.poll_events()
    glfw.terminate()


if __name__ == '__main__':
    pytest.main()
