#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Displays information about opengl
'''
import glfw
from glfw import gl


if not glfw.init():
    raise RuntimeError('Could not initialize GLFW')

major, minor = version = (3, 2)
glfw.window_hint(glfw.FOCUSED, gl.GL_FALSE)
glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
profile = glfw.OPENGL_ANY_PROFILE if version < (3, 2) else glfw.OPENGL_CORE_PROFILE
glfw.window_hint(glfw.OPENGL_PROFILE, profile)
# Setup forward compatibility if able
forward_compat = gl.GL_FALSE if version < (3, 0) else gl.GL_TRUE
glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, forward_compat)
#  Keep the window invisible
glfw.window_hint(glfw.VISIBLE, gl.GL_FALSE)
win = glfw.create_window()
glfw.make_context_current(win)


def display_info(version=(3, 2)):
    # Display basic information
    print('OpenGL Version: {}'.format(gl.get_string(gl.VERSION)))
    print('OpenGL Vendor: {}'.format(gl.get_string(gl.VENDOR)))
    print('OpenGL Renderer: {}'.format(gl.get_string(gl.RENDERER)))
    print('OpenGL GLSL: {}'.format(gl.get_string(gl.SHADING_LANGUAGE_VERSION)))

    # Display Extension information
    if version < (3, 1):
        extension_count = gl.glGetIntegerv(gl.EXTENSIONS)
        for index in range(extension_count):
            extension_string = gl.get_string(gl.EXTENSIONS, index)
            print('OpenGL Extension Supported: {}'.format(extension_string))

    # Display GLSL Versions
    if version >= (4, 3):
        glsl_version_count = gl.glGetIntegerv(gl.NUM_SHADING_LANGUAGE_VERSIONS)
        for index in range(glsl_version_count):
            glsl_version = gl.get_string(gl.SHADING_LANGUAGE_VERSION, index)
            print('OpenGL GLSL Supported: {}'.format(glsl_version))

display_info()

glfw.terminate()
