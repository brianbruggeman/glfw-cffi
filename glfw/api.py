# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function,  # noqa
                        unicode_literals)

import os
import sys
from collections import namedtuple

# Import core and then import core functionality so we can override
# functions as desired within api but still retain the original api if
# really necessary
from . import raw
from .raw import core, decorators, gl, header_path, snake  # noqa

# Add snake-case python-friendly functions to local globals
for k, v in snake.__dict__.items():
    globals()[k] = v
ffi = raw._ffi
raw_glfw = raw._glfw


###############################################################################
# Hand written GLFW-CFFI API
###############################################################################
def get_include():
    '''Returns header_path found during initialization'''
    global header_path
    include_path = header_path
    if include_path is not None:
        while include_path not in ['/', '']:
            if include_path.split(os.path.sep)[-1] == 'include':
                break
            include_path = os.path.dirname(include_path)
    return include_path


def create_window(width=640, height=480, title="Untitled", monitor=None, share=None):
    '''Creates a window

    If a monitor is specified, then by default the application will
    be full-screen.

    Context is used when state from one window needs to be transferred
    to the new window.  A GlfwWindow * can be used for context.
    This is common when switching between full-screen and windowed
    mode.  During this operation, the window must be destroyed and
    re-created.
    '''
    monitors = get_monitors()
    if isinstance(monitor, Monitor):
        monitor = monitor.handle
    elif isinstance(monitor, int) and monitor < len(monitors):
        # monitor is an index
        monitor = monitors[monitor].handle or raw._ffi.NULL
    elif isinstance(monitor, str):
        # monitor is the name of a monitor
        if monitor.lower() == 'primary':
            monitor = snake.get_primary_monitor()
        else:
            monitor_matches = [m for m in monitors if m.name == monitor]
            # Pick the first one on multiple matches
            for monitor in monitor_matches:
                monitor = monitor.handle
                break
            if not isinstance(monitor, raw._ffi.CData):
                monitor = raw._ffi.NULL
    if monitor is None:
        monitor = core.glfwGetPrimaryMonitor()
    if share is None:
        share = raw._ffi.NULL
    if sys.version.startswith('3'):
        farg = raw._ffi.new('char []', bytes(title.encode('utf-8')))
        title = farg
    args = (
        width,
        height,
        title,
        monitor or raw._ffi.NULL,
        share or raw._ffi.NULL
    )
    win = core.glfwCreateWindow(*args)
    if win == raw._ffi.NULL:
        win = None
        args = {
            'width': width,
            'height': height,
            'title': ffi_string(title),
            'monitor': monitor,
            'share': share,
        }
        raise RuntimeError('Could not create window with args: {}'.format(args))
    return win


Resolution = namedtuple('Resolution', ('width', 'height'))
Position = namedtuple('Position', ('x', 'y'))
Size = namedtuple('Size', ('width', 'height'))


class Monitor(object):
    '''Python wrapper for GLFW Monitor

    Note: Monitors cannot be updated, only read.  GLFW intentionally
    made the Monitor data structure opaque, so only functions can be
    used to read the Monitor information rather than actually
    referencing individual properties.  So this particular data
    structure is meant to be referenced but not created.

    Args:
        handle(cffi.cdata): Monitor handle provided by the GLFW api
    '''

    def __init__(self, handle=None):
        if handle is None:
            handle = snake.get_primary_monitor()
        self.handle = handle

    @property
    def connected(self):
        count = ffi.new('int *')
        monitor_list = core.get_monitors(count)
        monitor_list = [monitor_list[index] for index in range(count[0])]
        return self.handle in monitor_list

    @property
    def height(self):
        return self.resolution.height

    @property
    def name(self):
        name = None
        if self.connected:
            name = snake.get_monitor_name(self.handle)
        return name

    @property
    def position(self):
        position = Position(None, None)
        if self.connected:
            position = snake.get_monitor_pos(self.handle)
            position = Position(position[0], position[1])
        return position

    @property
    def primary(self):
        primary = None
        if self.connected:
            primary = True if snake.get_primary_monitor() == self.handle else False
        return primary

    @property
    def resolution(self):
        resolution = Resolution(None, None)
        if self.connected:
            modes = snake.get_video_mode(self.handle)
            resolution = Resolution(modes[0].width, modes[0].height)
        return resolution

    @property
    def rotated(self):
        return self.width < self.height

    @property
    def size(self):
        size = Size(None, None)
        if self.connected:
            size = snake.get_monitor_physical_size(self.handle)
            size = Size(size[0], size[1])
        return size

    @property
    def width(self):
        return self.resolution.width

    def __repr__(self):
        cname = self.__class__.__name__
        width, height = self.resolution
        primary = '*' if self.primary else ' ' if self.connected else '?'
        name = self.name.decode("utf-8")
        string = '<{cname} {primary} [{width}, {height}] {name}>'
        string = string.format(cname=cname, primary=primary, width=width, height=height, name=name)
        return string


def get_monitors():
    '''Returns monitors connected'''
    count = raw._ffi.new('int *')
    monitors = []
    _monitors = snake.get_monitors(count)
    for index in range(count[0]):
        monitor = Monitor(_monitors[index])
        monitors.append(monitor)
    return monitors


###############################################################################
# Special error handler callback
###############################################################################
_error_callback_wrapper = None


def set_error_callback(func):
    '''Wraps the error callback function for GLFW and sets the callback function
    for the entire program'''

    # decorators is actually created in a hacky way (see: _initialize_module)
    # This may flub any static checking, but it still runs
    @decorators.error_callback  # noqa
    def wrapper(error, description):
        return func(error, ffi.string(description))
    global _error_callback_wrapper
    _error_callback_wrapper = wrapper
    raw_glfw.glfwSetErrorCallback(wrapper)


###############################################################################
# Special helper functions
###############################################################################
def ffi_string(cdata):
    '''Converts char * cdata into a python string'''
    if isinstance(cdata, ffi.CData):
        if 'char' in ffi.typeof(cdata).cname:
            cdata = ffi.string(cdata)
    return cdata


def get_key_string(key):
    '''Returns the name of a key'''
    val = 'KEY_'
    globs = dict(globals().items())
    lookup = {v: k.replace(val, '').lower() for k, v in globs.items() if k.startswith(val)}
    string = lookup.get(key, key)
    return string


def get_mod_string(mods):
    '''Returns the name of a modifier'''
    val = 'MOD_'
    lookup = {v: k.replace(val, '').lower() for k, v in globals().items() if k.startswith(val)}
    string = '+'.join(sorted({v for m, v in lookup.items() if m & mods}))
    return string


def get_mouse_button_string(button):
    '''Returns the name of a modifier'''
    val = 'MOUSE_BUTTON_'
    lookup = {v: k.replace(val, '').lower() for k, v in sorted(globals().items()) if k.startswith(val)}
    string = lookup.get(button, button)
    return string


def get_action_string(action):
    '''Returns the name of a modifier'''
    options = ['RELEASE', 'PRESS', 'REPEAT']
    data = {v: k.lower() for k, v in globals().items() if k in options}
    return data.get(action, action)
