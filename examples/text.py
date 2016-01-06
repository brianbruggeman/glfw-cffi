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
OpenGL.ERROR_CHECKING = False
import glfw
import OpenGL.GL as gl


def on_display(data, height, texid, base):
    gl.glClearColor(0, 0, 0, 1)
    gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texid)
    gl.glColor(1, 1, 1, 1)
    gl.glPushMatrix()
    padding = 5
    gl.glTranslate(padding, height-padding, 0)
    gl.glPushMatrix()
    gl.glListBase(base+1)
    gl.glCallLists(data)
    gl.glPopMatrix()
    gl.glPopMatrix()


@glfw.decorators.window_size_callback
def on_resize(win, width, height):
    fb_width, fb_height = glfw.get_framebuffer_size(win)
    gl.glViewport(0, 0, fb_width, fb_height)
    gl.glLoadIdentity()


@glfw.decorators.framebuffer_size_callback
def on_framebuffer_resize(win, width, height):
    gl.glViewport(0, 0, width, height)
    gl.glLoadIdentity()


@glfw.decorators.key_callback
def on_key(win, key, code, action, mods):
    if key == glfw.KEY_ESCAPE:
        glfw.set_window_should_close(win, gl.GL_TRUE)


@glfw.decorators.mouse_button_callback
def on_mouse_button(win, button, action, mods):
    glfw.set_window_should_close(win, gl.GL_TRUE)


def make_font(filename, size, texid, base):
    '''Rasterizes font to a bitmap'''
    # Load font  and check it is monotype
    face = ft.Face(filename)
    face.set_char_size(size*64)
    if not face.is_fixed_width:
        raise 'Font is not monotype'

    # Determine largest glyph size
    width, height, ascender, descender = 0, 0, 0, 0
    for c in range(32, 128):
        face.load_char(chr(c), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
        bitmap = face.glyph.bitmap
        width = max(width, bitmap.width)
        ascender = max(ascender, face.glyph.bitmap_top)
        descender = max(descender, bitmap.rows-face.glyph.bitmap_top)
    height = ascender+descender

    # Generate texture data
    Z = np.zeros((height*6, width*16), dtype=np.ubyte)
    for j in range(6):
        for i in range(16):
            face.load_char(chr(32+j*16+i), ft.FT_LOAD_RENDER | ft.FT_LOAD_FORCE_AUTOHINT)
            bitmap = face.glyph.bitmap
            x = i*width + face.glyph.bitmap_left
            y = j*height + ascender - face.glyph.bitmap_top
            Z[y:y+bitmap.rows, x:x+bitmap.width].flat = bitmap.buffer

    # Bound texture
    texid = gl.glGenTextures(1)
    gl.glBindTexture(gl.GL_TEXTURE_2D, texid)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
    gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)
    gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_ALPHA, Z.shape[1], Z.shape[0], 0,
                    gl.GL_ALPHA, gl.GL_UNSIGNED_BYTE, Z)

    # Generate display lists
    dx, dy = width/float(Z.shape[1]), height/float(Z.shape[0])
    base = gl.glGenLists(8*16)
    for i in range(8*16):
        c = chr(i)
        x = i % 16
        y = i//16-2
        gl.glNewList(base+i, gl.GL_COMPILE)
        if (c == '\n'):
            gl.glPopMatrix()
            gl.glTranslatef(0, -height, 0)
            gl.glPushMatrix()
        elif (c == '\t'):
            gl.glTranslatef(4*width, 0, 0)
        elif (i >= 32):
            gl.glBegin(gl.GL_QUADS)
            gl.glTexCoord2f((x)*dx, (y+1)*dy), gl.glVertex(0,     -height)
            gl.glTexCoord2f((x)*dx, (y)*dy), gl.glVertex(0,     0)
            gl.glTexCoord2f((x+1)*dx, (y)*dy), gl.glVertex(width, 0)
            gl.glTexCoord2f((x+1)*dx, (y+1)*dy), gl.glVertex(width, -height)
            gl.glEnd()
            gl.glTranslatef(width, 0, 0)
        gl.glEndList()
    return texid


def main(**options):
    if not glfw.init():
        raise RuntimeError('Could not initialize GLFW')

    texid = 0
    base = 0
    width = options.get('width')
    height = options.get('height')
    font = options.get('font')
    font_size = options.get('font_size')
    win = glfw.create_window(
        title=options.get('title'),
        height=height,
        width=width
    )
    glfw.set_key_callback(win, on_key)
    glfw.set_mouse_button_callback(win, on_mouse_button)
    glfw.set_window_size_callback(win, on_resize)
    glfw.set_framebuffer_size_callback(win, on_framebuffer_resize)
    glfw.make_context_current(win)

    # determine max framebuffer size
    fb_width, fb_height = glfw.get_framebuffer_size(win)

    # Setup for font
    gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
    gl.glEnable(gl.GL_DEPTH_TEST)
    gl.glEnable(gl.GL_BLEND)
    gl.glEnable(gl.GL_COLOR_MATERIAL)
    gl.glColorMaterial(gl.GL_FRONT_AND_BACK, gl.GL_AMBIENT_AND_DIFFUSE)
    gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)
    gl.glEnable(gl.GL_TEXTURE_2D)
    texid = make_font(font, font_size, texid, base)

    # Run the resize code to setup the display
    gl.glViewport(0, 0, fb_width, fb_height)
    gl.glMatrixMode(gl.GL_PROJECTION)
    gl.glLoadIdentity()
    gl.glOrtho(0, fb_width, 0, fb_height, -1, 1)
    gl.glMatrixMode(gl.GL_MODELVIEW)
    gl.glLoadIdentity()

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

    while not glfw.window_should_close(win):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        # Use the framebuffer height to prevent viewport issues when moving from
        #  LoDPI to HiDPI in a multiple monitor, multiple-dpi display scenario
        on_display(data, fb_height, texid, base)
        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()


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
