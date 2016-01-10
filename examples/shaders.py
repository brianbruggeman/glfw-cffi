#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import division
import ctypes
from random import random as rand
from textwrap import dedent as dd


import numpy as np
import OpenGL
OpenGL.ERROR_CHECKING = True
import glfw
from glfw import gl


# ######################################################################
# Data
# ######################################################################
width, height = 640, 480
major, minor = (4, 1)
draw_array = True

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
mode_index = modes.index(gl.GL_TRIANGLE_STRIP)

fills = [
    gl.GL_FILL,
    gl.GL_POINT,
    gl.GL_LINE
]
fill_index = fills.index(gl.GL_POINT)

pt = 0.5
# vertices = np.array((
#     (-pt, pt, 0.0),
#     (0.0, pt, 0.0),
#     (pt, pt, 0.0),
#     (pt, 0.0, 0.0),
#     (0.0, 0.0, 0.0),
#     (-pt, 0.0, 0.0),
#     (-pt, -pt, 0.0),
#     (0.0, -pt, 0.0),
#     (pt, -pt, 0.0),
# ), dtype=np.float32)

vertices = np.array((
    (0, pt),
    (pt, -pt),
    (-pt, -pt),
), dtype=np.float32)

# rgb = 3
# colors = np.array([
#     [rand() for _ in range(rgb)]  # vec3 of colors
#     for v in vertices  # one for every index
# ], dtype=np.float32)

indices = np.array([
    0, 1, 2
    # 4, 2, 1,
    # 0, 2, 3,
    # 0, 3, 4,
    # 0, 4, 5,
], dtype=np.uint32)

# data = np.zeros(
#     len(vertices),
#     dtype=[
#         ("position", np.float32, len(vertices[0])),
#         ("color", np.float32, len(colors[0])),
#     ]
# )

# # Interleave vertex data for position and color
# data['position'] = vertices
# data['color'] = colors

vshader = '''
    #version 410

    in vec2 position;
    in vec3 color;

    out vec3 vcolor;

    void main () {
        gl_Position = vec4(position.xy, 0.0, 1.0);
        vcolor = color;
    }
    '''

fshader = '''
    #version 410

    in vec3 vcolor;
    out vec4 frag_color;

    void main () {
        // frag_color = vec4(vcolor.xyz * 3.5, 1.0);
        frag_color = vec4(0.2, 1.0, 0.4, 1.0);
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
    global vertices_buffer_id
    global vertices
    if action in [glfw.PRESS]:
        if key in [glfw.KEY_ESCAPE, glfw.KEY_Q]:
            # Quit
            glfw.set_window_should_close(win, gl.GL_TRUE)
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
        elif key == glfw.KEY_A:
            # Toggle between drawing element with an indices and an array
            draw_array = False if draw_array else True
            gl.glEnableVertexAttribArray(0)
            if not draw_array:
                gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
            gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
            gl.glVertexAttribPointer(0, len(vertices[0]), gl.GL_FLOAT, False, 0, None)
            print('Drawing array: {}'.format(draw_array))


# ######################################################################
# Setup OpenGL Context
glfw.init()
glfw.core.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
glfw.core.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
glfw.core.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
glfw.core.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
win = glfw.create_window(title='OpenGL 4.1 Rendering', width=width, height=height)
glfw.core.set_key_callback(win, on_key)
glfw.core.make_context_current(win)

gl.glEnable(gl.GL_DEPTH_TEST)
gl.glDepthFunc(gl.GL_LESS)

# ######################################################################
# Setup VBO and VAO
vertices_buffer_id = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
gl.glBufferData(gl.GL_ARRAY_BUFFER, vertices.nbytes, vertices.flatten(), gl.GL_STATIC_DRAW)

indices_buffer_id = gl.glGenBuffers(1)
gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)

vao = gl.glGenVertexArrays(1)
gl.glBindVertexArray(vao)

# Build pipeline
program = gl.glCreateProgram()
vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)

# Build and compile Shaders
gl.glShaderSource(vertex_shader, dd(vshader))
gl.glShaderSource(fragment_shader, dd(fshader))

gl.glCompileShader(vertex_shader)
gl.glCompileShader(fragment_shader)

# gl.glBindAttribLocation(program, 0, "position")
# gl.glBindAttribLocation(program, 1, "color")

gl.glAttachShader(program, vertex_shader)
gl.glAttachShader(program, fragment_shader)
gl.glLinkProgram(program)
gl.glUseProgram(program)

gl.glDetachShader(program, vertex_shader)
gl.glDetachShader(program, fragment_shader)
gl.glUseProgram(program)

# stride = data.strides[0]
# offset = ctypes.c_void_p(0)
# loc = gl.glGetAttribLocation(program, "position")
# gl.glEnableVertexAttribArray(loc)
# gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
# gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
# gl.glVertexAttribPointer(loc, len(data['position'][0]), gl.GL_FLOAT, False, stride, offset)

gl.glEnableVertexAttribArray(0)
# gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
gl.glVertexAttribPointer(0, len(vertices[0]), gl.GL_FLOAT, False, 0, None)

# offset = ctypes.c_void_p(data["position"].itemsize)
# loc = gl.glGetAttribLocation(program, "color")
# gl.glEnableVertexAttribArray(loc)
# gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, indices_buffer_id)
# gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vertices_buffer_id)
# gl.glVertexAttribPointer(loc, len(data['color'][0]), gl.GL_FLOAT, False, stride, offset)


# ######################################################################
# Initialize scene
gl.glClearColor(0.1, 0.1, 0.1, 1.0)

# ######################################################################
# Render
while not glfw.core.window_should_close(win):
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glPolygonMode(gl.GL_FRONT_AND_BACK, fills[fill_index])

    gl.glBindVertexArray(vao)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, vertices.itemsize, gl.GL_FLOAT, False, 0, None)
    # draw vertices 0-3 from the currently bound VAO with current in-use shader
    if draw_array:
        gl.glDrawArrays(modes[mode_index], len(indices), gl.GL_UNSIGNED_INT, None)
    else:
        gl.glDrawElements(modes[mode_index], len(indices), gl.GL_UNSIGNED_INT, None)

    glfw.core.swap_buffers(win)
    glfw.core.poll_events()


# ######################################################################
# Cleanup
gl.glUseProgram(0)
glfw.core.terminate()
