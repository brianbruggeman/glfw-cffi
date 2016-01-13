#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import ctypes
from random import random as rand
from textwrap import dedent as dd
from pprint import pprint as pp

import numpy as np
import OpenGL
OpenGL.ERROR_CHECKING = True
import glfw
from glfw import gl


# ######################################################################
# Data
# ######################################################################
title = 'OpenGL 4.1 Rendering'
width, height = 640, 480
major, minor = (4, 1)
draw_array = False
use_data = True

modes = sorted([
    gl.GL_POINTS,
    gl.GL_LINES,
    gl.GL_LINE_LOOP,
    gl.GL_LINE_STRIP,
    gl.GL_LINES_ADJACENCY,
    gl.GL_LINE_STRIP_ADJACENCY,
    # gl.GL_QUADS,
    gl.GL_TRIANGLES,
    gl.GL_TRIANGLE_STRIP,
    gl.GL_TRIANGLE_FAN,
    gl.GL_TRIANGLE_STRIP_ADJACENCY,
    gl.GL_TRIANGLES_ADJACENCY,
    # gl.GL_PATCHES,
])
mode_index = modes.index(gl.GL_TRIANGLES)

fills = [
    gl.GL_FILL,
    gl.GL_POINT,
    gl.GL_LINE
]
fill_index = fills.index(gl.GL_LINE)

pt = 0.5

vertices = np.array([
    (x, y) for x in [-pt, 0, pt] for y in [-pt, 0, pt]
    # (0.0, pt),
    # (-pt, -pt),
    # (pt, -pt),
    # (pt, pt),
    # (-pt, pt),
], dtype=np.float32)

indices = np.array([
    # index for index in range(vertices.shape[0])
    5, 6, 0,
    5, 2, 0,
    5, 8, 6,
], dtype=np.uint32)

# Generate some colors for the points
rgb = 3
colors = np.array([
    # [rand() for _ in range(rgb)]  # vec3 of colors
    # for v in vertices  # one for every vertex
    (1.0, 0.0, 0.0),
    (0.0, 1.0, 0.0),
    (0.0, 0.0, 1.0),

    (1.0, 0.0, 1.0),
    (0.0, 1.0, 1.0),
    (1.0, 1.0, 0.0),

    (0.5, 0.5, 0.5),
    (0.5, 0.5, 0.0),
    (0.0, 0.5, 0.5),
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

for i, d in enumerate(data):
    print(i, d)


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
        // frag_colour = vec4(0.5, 1.0, 0.5, 1.0);
    }
    '''


# ######################################################################
# Helper functions
@glfw.decorators.key_callback
def on_key(win, key, code, action, mods):
    '''Handles keyboard event'''
    global mode_index
    global fill_index
    global draw_array
    global indices_buffer_id
    global vertices
    global colors
    global data
    global use_data
    if action in [glfw.PRESS]:
        if key in [glfw.KEY_ESCAPE, glfw.KEY_Q]:
            # Quit
            glfw.core.set_window_should_close(win, gl.GL_TRUE)
        elif key == glfw.KEY_M:
            # Update draw mode (points, lines, triangles, quads, etc.)
            if mods & glfw.MOD_SHIFT:
                mode_index = mode_index - 1 if mode_index - 1 >= 0 else len(modes) - 1
            else:
                mode_index = mode_index + 1 if mode_index + 1 < len(modes) else 0
            print('New mode: {}'.format(modes[mode_index]))
        elif key == glfw.KEY_W:
            # Update fill mode (wireframe, solid, points)
            if mods & glfw.MOD_SHIFT:
                fill_index = fill_index - 1 if fill_index - 1 >= 0 else len(fills) - 1
            else:
                fill_index = fill_index + 1 if fill_index + 1 < len(fills) else 0
            print('New fill: {}'.format(fills[fill_index]))
        elif key == glfw.KEY_SPACE:
            # Randomize colors
            colors = np.array([
                [rand() for _ in range(rgb)]  # vec3 of colors
                for v in vertices  # one for every index
            ], dtype=np.float32)
            data['color'] = colors
            print(data)


def compile(shader):
    '''Compiles a shader'''


def compile_and_link_program(vertex_shader, fragment_shader, geometry_shader=None,
                             tesellation_evaluation=None, tesellation_control=None):
    '''Creates a program from the shaders provided'''
    shaders = {
        'v': gl.create_shader(gl.VERTEX_SHADER),
        'f': gl.create_shader(gl.FRAGMENT_SHADER),
    }
    program = gl.create_program()



# ######################################################################
# Setup OpenGL Context
glfw.core.init()
glfw.core.window_hint(glfw.SAMPLES, 4)
glfw.core.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
glfw.core.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
glfw.core.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.core.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
# glfw.core.window_hint(glfw.DECORATED, False)
glfw.core.window_hint(glfw.RED_BITS, 8)
glfw.core.window_hint(glfw.GREEN_BITS, 8)
glfw.core.window_hint(glfw.BLUE_BITS, 8)
glfw.core.window_hint(glfw.ALPHA_BITS, 8)
glfw.core.window_hint(glfw.DEPTH_BITS, 24)

win = glfw.create_window(title=title, width=width, height=height)
glfw.core.set_key_callback(win, on_key)
glfw.core.make_context_current(win)

gl.glEnable(gl.GL_DEPTH_TEST)
gl.glDepthFunc(gl.GL_LESS)

# Build pipeline
program = gl.glCreateProgram()
vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

# Build and compile Shaders
gl.glShaderSource(vertex_shader, dd(vshader))
gl.glShaderSource(fragment_shader, dd(fshader))

gl.glCompileShader(vertex_shader)
gl.glCompileShader(fragment_shader)

# Check for compilation errors
v_result = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
v_log = gl.glGetShaderiv(vertex_shader, gl.GL_INFO_LOG_LENGTH)
if v_log > 0:
    v_error_message = gl.glGetShaderInfoLog(vertex_shader)
    error_message = v_error_message.split(':')[-1].strip()
    print('ERROR: Vertex Shader Compilation | {}'.format(error_message))

f_result = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
f_log = gl.glGetShaderiv(fragment_shader, gl.GL_INFO_LOG_LENGTH)
if f_log > 0:
    f_error_message = gl.glGetShaderInfoLog(fragment_shader)
    error_message = f_error_message.split(':')[-1].strip()
    print('ERROR: Fragment Shader Compilation | {}'.format(error_message))

# Link Shaders to Program
gl.glAttachShader(program, vertex_shader)
gl.glAttachShader(program, fragment_shader)
gl.glLinkProgram(program)

p_result = gl.glGetProgramiv(program, gl.GL_LINK_STATUS)
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


# ######################################################################
# Initialize scene
gl.glClearColor(0.1, 0.1, 0.1, 1.0)

# ######################################################################
# Setup VBO and VAO
vao = gl.glGenVertexArrays(1)
buffer_id = gl.glGenBuffers(1)
indices_buffer_id = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, buffer_id)

gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices.flatten(), gl.GL_STATIC_DRAW)


# ######################################################################
# Render
while not glfw.window_should_close(win):
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, fills[fill_index])
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

    gl.glDrawElements(modes[mode_index], len(indices), gl.GL_UNSIGNED_INT, None)

    # Cleanup
    gl.glDisableVertexAttribArray(vao)
    # Standard Loop Event handling
    glfw.core.swap_buffers(win)
    glfw.core.poll_events()


# ######################################################################
# Cleanup
gl.glUseProgram(0)
glfw.core.terminate()
