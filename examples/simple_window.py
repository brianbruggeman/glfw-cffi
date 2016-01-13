#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Displays a simple window using glfw-cffi.
'''
from __future__ import print_function
from __future__ import division

import glfw
from OpenGL import GL as gl


windows = {}


def error_callback(error, description):
    print('{}: {}'.format(error, description))

glfw.set_error_callback(error_callback)


@glfw.decorators.key_callback
def on_key(win, key, code, action, mods):
    '''Converts key into an event'''
    if key in [glfw.KEY_ESCAPE] and action in [glfw.PRESS]:
        glfw.set_window_should_close(win, gl.GL_TRUE)


def render_scene(width, height, ratio):
    # Initial setup for scene
    gl.glViewport(0, 0, width, height)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glMatrixMode(gl.GL_MODELVIEW)
    left = -ratio  # Ratio needs to be a float
    right = ratio  # Ratio needs to be a float
    gl.glOrtho(left, right, -1.0, 1.0, 1.0, -1.0)
    gl.glLoadIdentity()
    # More logic here for additional scenes


def main():
    if not glfw.init():
        raise RuntimeError('Could not initialize glfw')

    monitor = glfw.get_primary_monitor()
    size = glfw.get_monitor_physical_size(monitor)
    if size[-1] == 0:
        size = (480, 640)
    ratio = size[0] / size[1]
    mode = glfw.get_video_mode(monitor)
    width, height = mode.width, mode.height
    global windows
    # Possible options; multiple windows is possible
    windows.update({
        # 'full_screen': glfw.create_window(title='Fullscreen', height=height, width=width, monitor=monitor),
        'window_01': glfw.create_window(title='01', height=height, width=width),
        # 'window_02': glfw.create_window(height, width, '02')
    })
    for win in windows.values():
        glfw.set_key_callback(win, on_key)
        glfw.make_context_current(win)

    # Event/render loop
    while not any(glfw.window_should_close(win) for win in windows.values()):
        render_scene(width, height, ratio)
        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()


if __name__ == '__main__':
    main()
