#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division
from pprint import pprint as pp

import pytest


def test_decorators():
    import glfw
    from glfw import gl
    assert glfw.init() == gl.TRUE

    glfw.window_hint(glfw.FOCUSED, False)
    glfw.window_hint(glfw.VISIBLE, False)
    win = glfw.create_window(title='Decorator test')
    glfw.make_context_current(win)

    @glfw.decorators.char_callback
    def on_char(win, codepoint):
        '''Handles unicode char callback

        This is useful for handling simple character strokes and text input
        '''
        pp('{}'.format(chr(codepoint)))

    @glfw.decorators.char_mods_callback
    def on_char_mods(win, codepoint, mods):
        '''Handles unicode char callback /w mods

        This is useful for handling simple character strokes and text input
        with modifiers
        '''
        msg = '+'.join('{}'.format(_) for _ in (chr(codepoint), glfw.get_mod_string(mods)))
        pp('{}'.format(msg))

    @glfw.decorators.cursor_enter_callback
    def on_cursor_focus(win, state):
        '''Cursor position upon entering client area'''
        state = 'Gained Focus' if state else 'Lost Focus'
        pp('Mouse Focus: {state}'.format(state=state))

    @glfw.decorators.drop_callback
    def on_file_drag_and_drop(win, count, paths):
        '''Handles drag and drop of file paths'''
        for some_path in range(count):
            path = paths[some_path]
            pp('Drag and dropped file: {}'.format(path))

    @glfw.decorators.error_callback
    def on_error(code, message):
        '''Handles an error callback event'''
        message = '{}: {}'.format(code, message)
        pp(message)

    @glfw.decorators.framebuffer_size_callback
    def on_framebuffer_resize(win, width, height):
        '''Handles a framebuffer resize event'''
        pp('New Framebuffer Size: ({width}, {height})'.format(width=width, height=height))

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
        pp(string)

    @glfw.decorators.monitor_callback
    def on_monitor(monitor, event=None):
        '''Handles monitor connect and disconnect'''
        state = 'Connected' if event else 'Disconnected'
        pp('Monitor {event}: {monitor}'.format(event=event, monitor=state))

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
        pp(string)

    @glfw.decorators.cursor_pos_callback
    def on_mouse_move(win, x, y):
        '''Mouse movement handler'''
        pp('Mouse position: ({x}, {y})'.format(x=x, y=y))

    @glfw.decorators.scroll_callback
    def on_scroll(win, x, y):
        '''Scrollback handler'''
        pp('Mouse scroll: ({x}, {y})'.format(x=x, y=y))

    @glfw.decorators.window_close_callback
    def on_window_close(win):
        '''Handles a window close event'''

    @glfw.decorators.window_focus_callback
    def on_window_focus(win, state):
        ''''''
        state = 'Regained Focus' if state else 'Lost Focus'
        pp('Window: {state}'.format(state=state))

    @glfw.decorators.window_iconify_callback
    def on_window_minimize(win, state):
        '''Handles window minimization/restore events'''
        state = 'Minimized' if state else 'Restored'
        pp('Window {state}: {win}'.format(state=state, win=win))

    @glfw.decorators.window_pos_callback
    def on_window_move(win, x, y):
        '''Handles window move event'''
        pp('New window position: ({x}, {y})'.format(x=x, y=y))

    @glfw.decorators.window_refresh_callback
    def on_window_refresh(win):
        '''Window refresh handler

        Called periodically or during window resize events'''
        pp('Refreshed window: {win}'.format(win=win))

    @glfw.decorators.window_size_callback
    def on_window_resize(win, width, height):
        '''Window resize handler'''
        pp('Window size: {width}x{height}'.format(width=width, height=height))

    glfw.set_char_callback(win, on_char)
    glfw.set_char_mods_callback(win, on_char_mods)
    glfw.set_cursor_enter_callback(win, on_cursor_focus)
    glfw.set_cursor_pos_callback(win, on_mouse_move)
    glfw.set_error_callback(on_error)
    glfw.set_key_callback(win, on_key)
    glfw.set_mouse_button_callback(win, on_mouse_button)
    glfw.set_scroll_callback(win, on_scroll)
    glfw.set_window_refresh_callback(win, on_window_refresh)
    glfw.set_window_size_callback(win, on_window_resize)
    glfw.set_window_pos_callback(win, on_window_move)
    glfw.set_window_close_callback(win, on_window_close)
    glfw.set_window_focus_callback(win, on_window_focus)
    glfw.set_window_iconify_callback(win, on_window_minimize)
    glfw.set_drop_callback(win, on_file_drag_and_drop)
    glfw.set_framebuffer_size_callback(win, on_framebuffer_resize)
    glfw.set_monitor_callback(on_monitor)


if __name__ == '__main__':
    pytest.main()
