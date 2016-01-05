#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Contains logic to produce a simple Window as a class rather than a set
of function calls

Usage:
    Window.py [options]

Options:
    -h --help           This message
    -q --quiet          Less messages
    -v --verbose        More messages
    -w --width WIDTH    Width of window [default: 640]
    -H --height HEIGHT  Height of window [default: 480]
    -t --title TITLE    Title of window [default: GLFW Example]
'''
import logging

import glfw
from OpenGL import GL as gl


log = logging.getLogger('Window')


class Window(object):

    def __init__(self, title='GLFW Example', height=480, width=640, init=None, render=None):
        if not glfw.init():
            raise RuntimeError('Could not initialize glfw')

        # Hinting must be run before window creation
        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 2)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)

        self.win = glfw.create_window(height=height, width=width, title=title)
        glfw.set_key_callback(self.win, self.on_key)
        glfw.set_mouse_button_callback(self.win, self.on_mouse_button)
        glfw.make_context_current(self.win)
        if init:
            init(self.win)
        else:
            gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        self.render = render

    def loop(self):
        '''Simplified loop'''
        while not glfw.window_should_close(self.win):
            if self.render:
                self.render(self.win)
            glfw.swap_buffers(self.win)
            glfw.poll_events()

    @staticmethod
    @glfw.decorators.key_callback
    def on_key(win, key, code, action, mods):
        '''Handles a key event'''
        if key in [glfw.KEY_ESCAPE] and action in [glfw.PRESS]:
            glfw.set_window_should_close(win, gl.GL_TRUE)
        # Display what just happened
        key = glfw.get_key_string(key)
        amapping = {'press': '+', 'release': '-', 'repeat': '*'}
        action = amapping.get(glfw.get_action_string(action))
        mods = glfw.get_mod_string(mods)
        string = '{}|{}'.format(action[0], '+'.join(str(_) for _ in (mods, key) if _))
        log.debug(string)

    @staticmethod
    @glfw.decorators.mouse_button_callback
    def on_mouse_button(win, button, action, mods):
        '''Handles a mouse button event'''
        # Not used here, but having the position where the mouse was at the
        #  time of the click can be useful.
        position = glfw.get_cursor_pos(win)
        # Handle button
        if button in [glfw.MOUSE_BUTTON_1] and action in [glfw.PRESS]:
            glfw.set_window_should_close(win, gl.GL_TRUE)
        # Display what just happened
        button = glfw.get_mouse_button_string(button)
        amapping = {'press': '+', 'release': '-', 'repeat': '*'}
        action = amapping.get(glfw.get_action_string(action))
        mods = glfw.get_mod_string(mods)
        position = '({:>.0f}, {:>.0f})'.format(*position)
        string = '{} {}|{}'.format(position, action[0], '+'.join(str(_) for _ in (mods, button) if _))
        log.debug(string)


def main(**options):
    width = int(options.get('width'))
    height = int(options.get('height'))
    title = options.get('title')
    window = Window(title=title, height=height, width=width)
    window.loop()
    glfw.terminate()


if __name__ == '__main__':
    from docopt import docopt

    def fix(option):
        option = option.lstrip('--')  # --optional-arg -> optional-arg
        option = option.lstrip('<').rstrip('>')  # <positional-arg> -> positional-arg
        option = option.replace('-', '_')  # hyphen-arg -> method_parameter
        return option

    options = {fix(k): v for k, v in docopt(__doc__).items()}
    if options.get('quiet'):
        logging.basicConfig(level=logging.WARNING)
    elif options.get('verbose'):
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    main(**options)
