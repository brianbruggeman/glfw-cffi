#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Showcases how GLFW-CFFI might be wrapped in a higher level Window class.

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
from __future__ import print_function

import logging
import threading

import OpenGL
# Turn off ERROR_CHECKING to improve OpenGL performance
#  This must be run before glfw is imported
OpenGL.ERROR_CHECKING = True
import glfw
# GLFW comes with a replacement for OpenGL which uses OpenGL but renames
#  the functions so they are snake_case and drops the GL_ prefix
#  from enumerations
import glfw.gl as gl


log = logging.getLogger('Window')


class Window(object):
    '''Wraps GLFW functions into a convenient package

    >>> win = Window(title='Example', width=1080, height=720)
    >>> win.loop()
    '''
    registry = {}

    @property
    def width(self):
        '''Window width'''
        width, height = glfw.get_window_size(self.win)
        return width

    @property
    def height(self):
        '''Window height'''
        width, height = glfw.get_window_size(self.win)
        return height

    @property
    def fb_width(self):
        '''Framebuffer width'''
        fb_width, fb_height = glfw.get_framebuffer_size(self.win)
        return fb_width

    @property
    def fb_height(self):
        '''Framebuffer height'''
        fb_width, fb_height = glfw.get_framebuffer_size(self.win)
        return fb_height

    def __init__(self, title='GLFW Example', height=480, width=640):
        # Determine available major/minor compatibility
        #  This contains init and terminate logic for glfw, so it must be run first
        major, minor = self.get_opengl_version()
        self.title = title

        # Lock is for thread aware Windows and opening, closing and garbage
        #  collection
        self.lock = threading.Lock()

        if not glfw.core.init():
            raise RuntimeError('Could not initialize glfw')

        # Hinting must be run before window creation
        glfw.core.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
        glfw.core.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
        glfw.core.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
        glfw.core.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.TRUE)

        # Generate window
        self.win = glfw.create_window(height=height, width=width, title=title)
        Window.registry[self.win] = self

        # Setup window callbacks: Must be run after creating an OpenGL window
        self.setup_callbacks()

        # Set context
        glfw.core.make_context_current(self.win)
        self.init()

    def __del__(self):
        '''Removes the glfw window'''
        glfw.core.set_window_should_close(self.win, gl.TRUE)
        # Wait for loop to end
        self.lock.acquire()
        glfw.destroy_window(self.win)
        self.lock.release()

    def get_opengl_version(self):
        '''Contains logic to determine opengl version.

        Only run this within initialization before running standard window code
        '''
        # Determine available major/minor compatibility
        #  This contains init and terminate logic for glfw, so it must be run first
        ffi = glfw._ffi
        opengl_version = None
        versions = [
            (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0),
            (3, 3), (3, 2), (3, 1), (3, 0),
            (2, 1), (2, 0),
            (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
        ]
        farg = ffi.new('char []', bytes(''.encode('utf-8')))
        title = farg

        if not glfw.core.init():
            glfw.terminate()
            raise RuntimeError('Could not initialize GLFW')

        for major, minor in versions:
            try:
                glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
                glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
                glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
                glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, gl.GL_TRUE)
                glfw.window_hint(glfw.VISIBLE, gl.GL_FALSE)
                glfw.window_hint(glfw.FOCUSED, gl.GL_FALSE)
                window = glfw.core.create_window(1, 1, title, ffi.NULL, ffi.NULL)
                if window != ffi.NULL:
                    glfw.destroy_window(window)
                    if opengl_version is None:
                        opengl_version = (major, minor)
            except Exception as e:
                import traceback as tb
                for line in tb.format_exc(e).split('\n'):
                    log.error(line)

        glfw.terminate()
        return opengl_version

    def init(self):
        '''Scene initialization'''
        gl.clear(gl.COLOR_BUFFER_BIT)

    def render(self):
        '''Empty scene'''

    def loop(self):
        '''Simplified loop'''
        self.lock.acquire()
        while not glfw.window_should_close(self.win):
            self.render()
            self.handle_buffers_and_events()
        self.lock.release()

    def handle_buffers_and_events(self):
        glfw.core.swap_buffers(self.win)
        glfw.core.poll_events()

    def setup_callbacks(self):
        '''Creates glfw callbacks for this window'''
        glfw.core.set_char_callback(self.win, self.on_char)
        glfw.core.set_char_mods_callback(self.win, self.on_char_mods)
        glfw.core.set_cursor_enter_callback(self.win, self.on_cursor_focus)
        glfw.core.set_cursor_pos_callback(self.win, self.on_mouse_move)
        glfw.core.set_error_callback(self.on_error)
        glfw.core.set_key_callback(self.win, self.on_key)
        glfw.core.set_mouse_button_callback(self.win, self.on_mouse_button)
        glfw.core.set_scroll_callback(self.win, self.on_scroll)
        glfw.core.set_window_refresh_callback(self.win, self.on_window_refresh)
        glfw.core.set_window_size_callback(self.win, self.on_window_resize)
        glfw.core.set_window_pos_callback(self.win, self.on_window_move)
        glfw.core.set_window_close_callback(self.win, self.on_window_close)
        glfw.core.set_window_focus_callback(self.win, self.on_window_focus)
        glfw.core.set_window_iconify_callback(self.win, self.on_window_minimize)
        glfw.core.set_drop_callback(self.win, self.on_file_drag_and_drop)
        glfw.core.set_framebuffer_size_callback(self.win, self.on_framebuffer_resize)
        glfw.core.set_monitor_callback(self.on_monitor)

    @staticmethod
    def cdata_to_pystring(cdata):
        '''Converts char * cdata into a python string'''
        return glfw.cdata_to_pystring(cdata)

    @staticmethod
    @glfw.decorators.char_callback
    def on_char(win, codepoint):
        '''Handles unicode char callback

        This is useful for handling simple character strokes and text input
        '''
        log.debug('{}'.format(chr(codepoint)))

    @staticmethod
    @glfw.decorators.char_mods_callback
    def on_char_mods(win, codepoint, mods):
        '''Handles unicode char callback /w mods

        This is useful for handling simple character strokes and text input
        with modifiers
        '''
        msg = '+'.join('{}'.format(_) for _ in (chr(codepoint), glfw.get_mod_string(mods)))
        log.debug('{}'.format(msg))

    @staticmethod
    @glfw.decorators.cursor_enter_callback
    def on_cursor_focus(win, state):
        '''Cursor position upon entering client area'''
        state = 'Gained Focus' if state else 'Lost Focus'
        log.debug('Mouse Focus: {state}'.format(state=state))

    @staticmethod
    @glfw.decorators.drop_callback
    def on_file_drag_and_drop(win, count, paths):
        '''Handles drag and drop of file paths'''
        for some_path in range(count):
            path = Window.cdata_to_pystring(paths[some_path])
            log.debug('Drag and dropped file: {}'.format(path))

    @staticmethod
    @glfw.decorators.error_callback
    def on_error(code, message):
        '''Handles an error callback event'''
        error_message = Window.cdata_to_pystring(message)
        message = '{}: {}'.format(code, error_message)
        log.error(message)

    @staticmethod
    @glfw.decorators.framebuffer_size_callback
    def on_framebuffer_resize(win, width, height):
        '''Handles a framebuffer resize event'''
        log.debug('New Framebuffer Size: ({width}, {height})'.format(width=width, height=height))

    @staticmethod
    @glfw.decorators.key_callback
    def on_key(win, key, code, action, mods):
        '''Handles a key event'''
        if key in [glfw.KEY_ESCAPE] and action in [glfw.PRESS]:
            glfw.set_window_should_close(win, gl.TRUE)
        # Display what just happened
        key = glfw.get_key_string(key)
        amapping = {'press': '+', 'release': '-', 'repeat': '*'}
        action = amapping.get(glfw.get_action_string(action))
        mods = glfw.get_mod_string(mods)
        string = '{}|{}'.format(action[0], '+'.join(str(_) for _ in (mods, key) if _))
        log.debug(string)

    @staticmethod
    @glfw.decorators.monitor_callback
    def on_monitor(monitor, event=None):
        '''Handles monitor connect and disconnect'''
        state = 'Connected' if event else 'Disconnected'
        log.debug('Monitor {event}: {monitor}'.format(event=event, monitor=state))

    @staticmethod
    @glfw.decorators.mouse_button_callback
    def on_mouse_button(win, button, action, mods):
        '''Handles a mouse button event'''
        # Not used here, but having the position where the mouse was at the
        #  time of the click can be useful.
        position = glfw.get_cursor_pos(win)
        # Handle button
        if button in [glfw.MOUSE_BUTTON_1] and action in [glfw.PRESS]:
            glfw.set_window_should_close(win, gl.TRUE)
        # Display what just happened
        button = glfw.get_mouse_button_string(button)
        amapping = {'press': '+', 'release': '-', 'repeat': '*'}
        action = amapping.get(glfw.get_action_string(action))
        mods = glfw.get_mod_string(mods)
        position = '({:>.0f}, {:>.0f})'.format(*position)
        string = '{} {}|{}'.format(position, action[0], '+'.join(str(_) for _ in (mods, button) if _))
        log.debug(string)

    @staticmethod
    @glfw.decorators.cursor_pos_callback
    def on_mouse_move(win, x, y):
        '''Mouse movement handler'''
        log.debug('Mouse position: ({x}, {y})'.format(x=x, y=y))

    @staticmethod
    @glfw.decorators.scroll_callback
    def on_scroll(win, x, y):
        '''Scrollback handler'''
        log.debug('Mouse scroll: ({x}, {y})'.format(x=x, y=y))

    @staticmethod
    @glfw.decorators.window_close_callback
    def on_window_close(win):
        '''Handles a window close event'''
        win = Window.registry.get(win)
        if win:
            win = win.title
        log.debug('Window closed: ({win})'.format(win=win))

    @staticmethod
    @glfw.decorators.window_focus_callback
    def on_window_focus(win, state):
        ''''''
        state = 'Regained Focus' if state else 'Lost Focus'
        log.debug('Window: {state}'.format(state=state))

    @staticmethod
    @glfw.decorators.window_iconify_callback
    def on_window_minimize(win, state):
        '''Handles window minimization/restore events'''
        state = 'Minimized' if state else 'Restored'
        log.debug('Window {state}: {win}'.format(state=state, win=win))

    @staticmethod
    @glfw.decorators.window_pos_callback
    def on_window_move(win, x, y):
        '''Handles window move event'''
        log.debug('New window position: ({x}, {y})'.format(x=x, y=y))

    @staticmethod
    @glfw.decorators.window_refresh_callback
    def on_window_refresh(win):
        '''Window refresh handler

        Called periodically or during window resize events'''
        log.debug('Refreshed window: {win}'.format(win=win))

    @staticmethod
    @glfw.decorators.window_size_callback
    def on_window_resize(win, width, height):
        '''Window resize handler'''
        log.debug('Window size: {width}x{height}'.format(width=width, height=height))


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
