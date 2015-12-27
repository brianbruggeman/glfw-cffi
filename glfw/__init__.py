#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ######################################################################
#  Wrapper file for Python GLFW CFFI library
#  Used GLFW v3.2 api
#  Created by Brian Bruggeman
#  Copyright (c) 2016
#
#  License:  This file is released as Apache 2.0 license.  However, at
#  your option, you may apply any free software license you choose
#  provided that you adhere to the free software license chosen and
#  additionally follow these three criteria:
#   a. list the author's name of this software as a contributor to your
#      final product
#   b. provide credit to your end user of your product or software without
#      your end user asking for where you obtained your software
#   c. notify the author of this software that you are using this software
#   d. in addition, if you believe there can be some benefit in providing
#      your changes upstream, you'll submit a change request.  While this
#      criteria is completely optional, please consider not being a dick.
# ######################################################################
from ctypes.util import find_library as _find_library
import fnmatch
import os
import re
import sys

from cffi import FFI

if sys.version[0] == 2:
    range = xrange

###############################################################################


def _get_function_declaration(line):
    found = None
    pattern = ''.join((
        r'^\s*(?P<result>([A-Za-z_0-9]+))\s+',
        r'(?P<func_name>([A-Za-z_0-9]+))',
        r'\((?P<args>(.*))\)\;\s*$'
    ))
    eng = re.compile(pattern)
    if all(_ in line for _ in ('(', ')', ';')):
        if '@' not in line and not line.lstrip(' ').startswith('typedef'):
            if eng.search(line.strip()):
                found = [group.groupdict() for group in eng.finditer(line)][0]
                func_name = found['func_name']
                found['snake_name'] = _camelToSnake(func_name.replace('glfw', ''))
    return found


def _fix_source(data):
    '''Remove directives since they are not supported.'''
    lines = []
    ignored_directives = (
        '#include',
        '#if', '#ifdef', '#endif', '#ifndef', '#else', '#elif',
        '#error', '#undef',
        'extern',
    )
    prev_line = ''
    defines = {}
    for lineno, line in enumerate(data.split('\n')):
        if line.lstrip(' ').startswith(ignored_directives):
            prev_line = line
            continue
        if not line.strip():
            prev_line = line
            continue
        if line.lstrip(' ').startswith('GLFWAPI'):
            line = line.replace('GLFWAPI ', '')
        if prev_line == '#ifdef __cplusplus':
            if line.strip() == '}':
                prev_line = line
                continue
        if line.lstrip(' ').startswith('#define'):
            found = re.search('^(\s*)\#define\s+([0-9A-Za-z_]+)\s*$', line)
            if found:
                continue
            else:
                found = re.search('^(\s*)\#define\s+([0-9A-Za-z_]+)\s*(.*)$', line)
                if found:
                    space, key, value = found.groups()
                    if len(space) > 0:
                        continue
                    if value.startswith('__'):
                        continue
                    elif value in defines:
                        old_value, value = value, defines[value]
                        line = line.replace(old_value, value)
                    defines[key] = value
        lines.append(line)
        prev_line = line
    if 'GLFW_TRUE' not in defines:
        lines.append('#define GLFW_TRUE 1')
    if 'GLFW_FALSE' not in defines:
        lines.append('#define GLFW_FALSE 0')
    return '\n'.join(lines)


def _wrap_func(ffi, func_decl, func):
    '''Wraps glfw functions with snake skins'''
    func_type = ffi.typeof(func)
    func_args = func_type.args
    func_res = func_type.result
    decl_args = func_decl['args']
    func_fields = []
    fields = set()
    for ctype, arg in zip(func_args, decl_args.split(',')):
        arg = arg.replace(ctype.cname, '').replace(ctype.cname.replace(' ', ''), '')
        arg = arg.strip()
        func_fields.append((arg, ctype))
    fields = dict(func_fields)

    def wrapper(*args, **kwds):
        retval = []
        if func_args:
            new_args = []
            func_kwds = {}
            for (fname, ftype), arg in zip(func_fields, args):
                if not isinstance(arg, ffi.CData) and ftype.kind not in ['primitive']:
                    farg = ffi.new(ftype.cname)
                    farg[0] = arg
                    arg = farg
                func_kwds[fname] = arg
            for kwd, val in kwds.items():
                if kwd in fields:
                    fname, ftype = fields[kwd]
                    if not isinstance(val, ffi.CData) and ftype.kind not in ['primitive']:
                        farg = ffi.new(ftype.cname)
                        farg[0] = val
                        val = farg
                    func_kwds[fname] = val
            for name, ftype in func_fields:
                val = func_kwds.get(name)
                if val is None:
                    if ftype.kind == 'pointer':
                        val = ffi.new(ftype.cname)
                        func_kwds[name] = val
                        retval.append(val)
                    else:
                        val = ffi.NULL
                new_args.append(val)
            if func_res.kind != 'void':
                retval = func(*new_args)
            else:
                func(*new_args)
        else:
            if func_res.kind != 'void':
                retval = func()
            else:
                func()
        if retval in [ffi.NULL, []]:
            retval = None
        elif isinstance(retval, list):
            retval = [l[0] for l in retval]
        return retval

    wrapper.__doc__ = func.__doc__
    if not wrapper.__doc__:
        if func_args:
            if func_res.kind != 'void':
                wrapper.__doc__ = '{result} {snake_name}({args})'.format(**func_decl)
            else:
                wrapper.__doc__ = '{snake_name}({args})'.format(**func_decl)
        else:
            if func_res.kind != 'void':
                wrapper.__doc__ = '{result} {snake_name}()'.format(**func_decl)
            else:
                wrapper.__doc__ = '{snake_name}()'.format(**func_decl)

    wrapper.__name__ = func_decl['snake_name']

    return wrapper


def _camelToSnake(string):
    '''Converts camelCase to snake_case'''
    pass01 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    final = re.sub('([a-z0-9])([A-Z])', r'\1_\2', pass01).lower()
    return final


# Modifies the module directly by introspection and loading up glfw
#  library and parsing glfw header file
def _initialize_module(ffi):
    glfw_library = None

    # First if there is an environment variable pointing to the library
    if 'GLFW_LIBRARY' in os.environ:
        GLFW_LIBRARY = os.environ['GLFW_LIBRARY']
        if os.path.exists():
            glfw_library = os.path.realpath(GLFW_LIBRARY)

    # Else, try to find it
    if glfw_library is None:
        ordered_library_names = ['glfw3', 'glfw']
        for library_name in ordered_library_names:
            glfw_library = _find_library(library_name)
            if glfw_library is not None:
                break

    # Else, we failed and exit
    if glfw_library is None:
        raise OSError('GLFW library not found')

    # Look for the header being used
    include_found = False
    include_path = glfw_library
    while include_path not in ['/', '']:
        if os.path.isdir(include_path):
            if 'include' in os.listdir(include_path):
                include_found = True
                break
        if not include_found:
            include_path = os.path.dirname(include_path)

    library_path = None
    for root, folders, files in os.walk(include_path):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            if 'include' not in filepath:
                continue
            if 'glfw' not in filepath.lower():
                continue
            if fnmatch.fnmatch(filename, 'glfw*.h'):
                library_path = filepath
                break
        if library_path:
            break

    # If library header was not found, then use the one provided in repo
    if library_path is None:
        source_path = os.path.dirname(__file__)
        source_path = os.path.join(source_path, 'glfw3.h')

    # Parse header
    with open(library_path, 'r') as f:
        source = _fix_source(f.read())
    ffi.cdef(source)

    # Create the direct c-library instance for glfw3
    _glfw = ffi.dlopen(glfw_library)

    # Create python equivalents of glfw functions
    funcs = {
        _camelToSnake(d.replace('glfw', '')): getattr(_glfw, d)
        for d in dir(_glfw)
        if hasattr(getattr(_glfw, d), '__call__')
    }

    # Auto-wrap functions to make the friendly to Python
    for line in source.split('\n'):
        func_decl = _get_function_declaration(line)
        if func_decl:
            snake_name = func_decl['snake_name']
            if snake_name in funcs:
                funcs[snake_name] = _wrap_func(ffi, func_decl, funcs[snake_name])
            else:
                func = getattr(_glfw, func_decl['func_name'], None)
                if func:
                    funcs[snake_name] = _wrap_func(ffi, func_decl, func)

    # Add functions to module
    globals().update(funcs)

    # Create Python equivalents of #defines
    defs = {
        d.replace('GLFW_', ''): getattr(_glfw, d)
        for d in dir(_glfw)
        if d.startswith('GLFW_')
    }

    # Add #defines to module
    globals().update(defs)

    # And finally keep the API the same for those that want to copy and
    #  paste from online C examples;  this is a straight pass-through
    camelCase = {
        d: getattr(_glfw, d)
        for d in dir(_glfw)
    }

    # Add standard API to module.  Note the lack of wrapping
    globals().update(camelCase)

    return ffi, _glfw

# Adds glfw3 functions to module namespace
_ffi, _glfw = _initialize_module(FFI())


###############################################################################
# Functions that needed to be addressed by hand
###############################################################################
def create_window(width=640, height=480, title="Untitled", monitor=None, context=None):
    '''Creates a window'''
    # Context is used when state from one window needs to be transferred
    #  to the new window.  A GlfwWindow * can be used for context.
    #  This is common when switching between full-screen and windowed
    #  mode.  During this operation, the window must be destroyed and
    #  re-created.
    if monitor is None:
        monitor = _ffi.NULL
    if context is None:
        context = _ffi.NULL
    args = (width, height, title, monitor, context)
    win = _glfw.glfwCreateWindow(*args)
    return win


###############################################################################
# Callback decorators
###############################################################################
char_callback = _ffi.callback('void (GLFWwindow*, unsigned int)')
cursor_enter_callback = _ffi.callback('void (GLFWwindow*, int)')
cursor_pos_callback = _ffi.callback('void (GLFWwindow*, double, double)')
error_callback = _ffi.callback('void (int, const char*)')
frame_buffersize_callback = _ffi.callback('void (GLFWwindow*, int, int)')
key_callback = _ffi.callback('void (GLFWwindow*, int, int, int, int)')
monitor_callback = _ffi.callback('void (GLFWmonitor*, int)')
mouse_button_callback = _ffi.callback('void (GLFWwindow*, int, int, int)')
scroll_callback = _ffi.callback('void (GLFWwindow*, double, double)')
window_close_callback = _ffi.callback('void (GLFWwindow*)')
window_focus_callback = _ffi.callback('void (GLFWwindow*, int)')
window_iconify_callback = _ffi.callback('void (GLFWwindow*, int)')
window_pos_callback = _ffi.callback('void (GLFWwindow*, int, int)')
window_refresh_callback = _ffi.callback('void (GLFWwindow*)')
window_size_callback = _ffi.callback('void (GLFWwindow*, int, int)')


###############################################################################
# Special error handler callback
###############################################################################
_error_callback_wrapper = None


def set_error_callback(func):
    @error_callback
    def wrapper(error, description):
        return func(error, _ffi.string(description))
    global _error_callback_wrapper
    _error_callback_wrapper = wrapper
    _glfw.glfwSetErrorCallback(wrapper)
