#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Creates a small window and displays text within that window.

Usage:
    text [options]

Options:
    -h --help            This message
    -H --height HEIGHT   Window height [default: 200]
    -W --width WIDTH     Window width [default: 300]
    -T --title TITLE     Window title [default: GLFW Text Rendering Demo]
    -t --text FILE       Text file to use to read text data
    -f --font FONT       Font to use [default: InputMono.ttf]
    -S --font-size SIZE  Size of font to use [default: 16]
'''
from __future__ import division

from textwrap import dedent as dd

import numpy as np
import freetype as ft
import OpenGL
# Turn off ERROR_CHECKING to improve OpenGL performance
#  This must be run before glfw is imported
OpenGL.ERROR_CHECKING = False
# glfwCreateWindow and glfwGetFrameBufferSize integrate with python more easily
#  when using the wrapped functions
import glfw
# GLFW comes with a replacement for OpenGL which uses OpenGL but renames
#  the functions so they are snake_case and drops the GL_ prefix
#  from enumerations
from glfw import gl


def on_display(data, height, texid, base):
    gl.clear_color(0, 0, 0, 1)
    gl.clear(gl.COLOR_BUFFER_BIT | gl.DEPTH_BUFFER_BIT)
    gl.bind_texture(gl.TEXTURE_2D, texid)
    gl.color(1, 1, 1, 1)
    gl.push_matrix()
    padding = 5
    gl.translate(padding, height - padding, 0)
    gl.push_matrix()
    gl.list_base(base + 1)
    gl.call_lists(data)
    gl.pop_matrix()
    gl.pop_matrix()


@glfw.decorators.window_size_callback
def on_resize(win, width, height):
    fb_width, fb_height = glfw.get_framebuffer_size(win)
    gl.viewport(0, 0, fb_width, fb_height)
    gl.load_identity()


@glfw.decorators.framebuffer_size_callback
def on_framebuffer_resize(win, width, height):
    gl.viewport(0, 0, width, height)
    gl.load_identity()


@glfw.decorators.key_callback
def on_key(win, key, code, action, mods):
    if key in [glfw.KEY_ESCAPE, glfw.KEY_Q]:
        # Quit
        glfw.core.set_window_should_close(win, gl.GL_TRUE)

@glfw.decorators.mouse_button_callback
def on_mouse_button(win, button, action, mods):
    glfw.core.set_window_should_close(win, gl.TRUE)


def make_font(filename, size, texid, base):
    '''Rasterizes font to a bitmap'''
    # Load font  and check it is monotype
    face = ft.Face(filename)
    face.set_char_size(size * 64)
    if not face.is_fixed_width:
        raise 'Font is not monotype'

    # Determine largest glyph size
    width, height, ascender, descender = 0, 0, 0, 0
    for c in range(32, 128):
        face.load_char(chr(c), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
        bitmap = face.glyph.bitmap
        width = max(width, bitmap.width)
        ascender = max(ascender, face.glyph.bitmap_top)
        descender = max(descender, bitmap.rows - face.glyph.bitmap_top)
    height = ascender + descender

    # Generate texture data
    Z = np.zeros((height * 6, width * 16), dtype=np.ubyte)
    flags = ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT
    for j in range(6):
        for i in range(16):
            face.load_char(chr(32 + j * 16 + i), flags)
            bitmap = face.glyph.bitmap
            x = i * width + face.glyph.bitmap_left
            y = j * height + ascender - face.glyph.bitmap_top
            Z[y:y + bitmap.rows, x:x + bitmap.width].flat = bitmap.buffer

    # Bound texture
    texid = gl.glGenTextures(1)
    gl.bind_texture(gl.TEXTURE_2D, texid)
    gl.tex_parameterf(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR)
    gl.tex_parameterf(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR)
    gl.tex_image_2d(gl.TEXTURE_2D, 0, gl.ALPHA,
                    Z.shape[1], Z.shape[0], 0,
                    gl.ALPHA, gl.UNSIGNED_BYTE, Z)

    # Generate display lists
    dx, dy = width / float(Z.shape[1]), height / float(Z.shape[0])
    base = gl.gen_lists(8 * 16)
    for i in range(8 * 16):
        c = chr(i)
        x = i % 16
        y = i // 16 - 2
        gl.new_list(base + i, gl.COMPILE)
        if (c == '\n'):
            gl.pop_matrix()
            gl.translatef(0, -height, 0)
            gl.push_matrix()
        elif (c == '\t'):
            gl.translatef(4 * width, 0, 0)
        elif (i >= 32):
            gl.begin(gl.QUADS)
            gl.tex_coord_2f((x) * dx, (y + 1) * dy), gl.vertex(0, -height)
            gl.tex_coord_2f((x) * dx, (y) * dy), gl.vertex(0, 0)
            gl.tex_coord_2f((x + 1) * dx, (y) * dy), gl.vertex(width, 0)
            gl.tex_coord_2f((x + 1) * dx, (y + 1) * dy), gl.vertex(width, -height)
            gl.end()
            gl.translatef(width, 0, 0)
        gl.end_list()
    return texid


def main(**options):
    if not glfw.core.init():
        raise RuntimeError('Could not initialize GLFW')

    texid = 0
    base = 0
    width = options.get('width')
    height = options.get('height')
    font = options.get('font')
    font_size = options.get('font_size')
    win = glfw.create_window(height=height, width=width, title=options.get('title'))
    glfw.core.set_key_callback(win, on_key)
    glfw.core.set_mouse_button_callback(win, on_mouse_button)
    glfw.core.set_window_size_callback(win, on_resize)
    glfw.core.set_framebuffer_size_callback(win, on_framebuffer_resize)
    glfw.core.make_context_current(win)

    # Determine max frame-buffer size for "this" display/monitor
    #  This keeps the text size consistent when moving across Low DPI
    #  and High DPI displays.
    fb_width, fb_height = glfw.core.get_framebuffer_size(win)

    # Setup OpenGL for font
    gl.tex_envf(gl.TEXTURE_ENV, gl.TEXTURE_ENV_MODE, gl.MODULATE)
    gl.enable(gl.DEPTH_TEST)
    gl.enable(gl.BLEND)
    gl.enable(gl.COLOR_MATERIAL)
    gl.color_material(gl.FRONT_AND_BACK, gl.AMBIENT_AND_DIFFUSE)
    gl.blend_func(gl.SRC_ALPHA, gl.ONE_MINUS_SRC_ALPHA)
    gl.enable(gl.TEXTURE_2D)
    # Generate a texture atlas for the font
    font_size = font_size * fb_width // width
    texid = make_font(font, font_size, texid, base)

    # Run the resize code to setup the display
    gl.viewport(0, 0, fb_width, fb_height)
    gl.matrix_mode(gl.PROJECTION)
    gl.load_identity()
    gl.ortho(0, fb_width, 0, fb_height, -1, 1)
    gl.matrix_mode(gl.MODELVIEW)
    gl.load_identity()

    # Setup what we'll display
    text_file = options.get('text')
    if os.path.exists(text_file):
        with open(text_file, 'r') as fd:
            text = fd.read()
    else:
        text = '\n'.join(l for l in dd(u'''
        Hello, World!
        On multiple lines.
        ''').split('\n') if l.strip())

    data = [ord(c) for c in text]

    while not glfw.core.window_should_close(win):
        gl.clear(gl.COLOR_BUFFER_BIT)
        # Use the framebuffer height to prevent viewport issues when moving from
        #  LoDPI to HiDPI in a multiple monitor, multiple-dpi display scenario
        on_display(data, fb_height, texid, base)
        glfw.core.swap_buffers(win)
        glfw.core.poll_events()

    glfw.core.terminate()


if __name__ == '__main__':
    import os
    from docopt import docopt

    def fix(option):
        '''Simplifies docopt options and allows them to be sent into a function'''
        option = option.lstrip('-')
        option = option.lstrip('<').rstrip('>')
        option = option.replace('-', '_')
        return option

    options = {fix(k): v for k, v in docopt(__doc__).items()}
    options['height'] = int(options.get('height'))
    options['width'] = int(options.get('width'))
    options['font_size'] = int(options.get('font_size'))
    options['font'] = os.path.abspath(options.get('font'))
    options['text'] = os.path.abspath(options.get('text')) if options.get('text') else ''

    main(**options)
