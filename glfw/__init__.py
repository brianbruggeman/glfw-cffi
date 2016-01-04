#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Wrapper file for Python GLFW CFFI library

Created by Brian Bruggeman
Copyright (c) 2016

Usage:

    >>> import glfw
    >>> if not glfw.init():
    ...     raise RuntimeError('Could not initialize glfw')
    >>> win = glfw.create_window(640, 480, 'Sample')
    >>> while (not glfw.window_should_close(win)):  # ctrl+c to break
    ...     # Render scene here
    ...     glfw.swap_buffers(win)  # by default, glfw is double buffered
    ...     glfw.poll_events()
    >>> glfw.terminate()


License:  This file is released as Apache 2.0 license.  However, at
your option, you may apply any free software license you choose
provided that you adhere to the free software license chosen and
additionally follow these three criteria:
 a. list the author's name of this software as a contributor to your
    final product
 b. provide credit to your end user of your product or software without
    your end user asking for where you obtained your software
 c. notify the author of this software that you are using this software
 d. in addition, if you believe there can be some benefit in providing
    your changes upstream, you'll submit a change request.  While this
    criteria is completely optional, please consider not being a dick.
'''
from ctypes.util import find_library as _find_library
import fnmatch
import imp
import os
import re
import sys

from cffi import FFI


if sys.version[0] == 2:
    range = xrange

modname = os.path.basename(os.path.dirname(__file__))

###############################################################################
__title__ = 'glfw-cffi'
__version__ = '0.1.2'
__author__ = 'Brian Bruggeman'
__email__ = 'brian.m.bruggeman@gmail.com'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2016 Brian Bruggeman'
__url__ = 'https://github.com/brianbruggeman/glfw-cffi.git'
__shortdesc__ = 'Foreign Function Interface wrapper for GLFW v3.x'


###############################################################################
def _get_function_declaration(line):
    found = None
    pattern = ''.join((
        r'^\s*(?P<result>(.*))\s+',
        r'(?P<func_name>(glfw[A-Za-z_0-9*]+))',
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

    # Auto-wrapper for cffi function call
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

    def rename_code_object(func, new_name):
        '''Magic bit so a stack trace and profiling doesn't identify wrapper
        as the function'''
        code_object = func.__code__
        function, code = type(func), type(code_object)
        co_code = code_object.co_code
        co_lnotab = code_object.co_lnotab
        if sys.version.startswith('3'):
            # co_code = int.from_bytes(co_code, byteorder=sys.byteorder)
            # print('co_code: {}'.format(co_code))
            co_lnotab = int.from_bytes(co_lnotab, byteorder=sys.byteorder)
            print('co_lnotab: {}'.format(co_lnotab))
        code_objects = (
            code_object.co_argcount,
            code_object.co_nlocals,
            code_object.co_stacksize,
            code_object.co_flags,
            co_code,
            code_object.co_consts,
            code_object.co_names,
            code_object.co_varnames,
            code_object.co_filename,
            new_name,
            code_object.co_firstlineno,
            co_lnotab,
            code_object.co_freevars,
            code_object.co_cellvars
        )
        new_func = function(
            code(*code_objects),
            func.__globals__, new_name, func.__defaults__, func.__closure__
        )
        return new_func

    # Newly wrapped function
    new_func = rename_code_object(wrapper, func_decl['snake_name'])

    docstring = func.__doc__
    if not docstring:
        if func_args:
            if func_res.kind != 'void':
                docstring = '{result} {snake_name}({args})'.format(**func_decl)
            else:
                docstring = '{snake_name}({args})'.format(**func_decl)
        else:
            if func_res.kind != 'void':
                docstring = '{result} {snake_name}()'.format(**func_decl)
            else:
                docstring = '{snake_name}()'.format(**func_decl)
    new_func.__doc__ = docstring
    # wrapper.__name__ = func_decl['snake_name']

    return new_func


def _camelToSnake(string):
    '''Converts camelCase to snake_case'''
    pass01 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    final = re.sub('([a-z0-9])([A-Z])', r'\1_\2', pass01).lower()
    return final


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
    globals()['glfw_library'] = glfw_library

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

    header_path = None
    for root, folders, files in os.walk(include_path):
        for filename in sorted(files):
            filepath = os.path.join(root, filename)
            if 'include' not in filepath:
                continue
            if 'glfw' not in filepath.lower():
                continue
            if fnmatch.fnmatch(filename, 'glfw*.h'):
                header_path = filepath
                break
        if header_path:
            break

    # If library header was not found, then use the one provided in repo
    if header_path is None:
        source_path = os.path.dirname(__file__)
        header_path = os.path.join(source_path, 'glfw3.h')

    globals()['header_path'] = header_path
    # Parse header
    with open(header_path, 'r') as f:
        source = _fix_source(f.read())
    ffi.cdef(source)

    # Create the direct c-library instance for glfw3
    _glfw = ffi.dlopen(glfw_library)

    # Create python equivalents of glfw functions
    funcs = {}
    camelCase = {}
    for d in dir(_glfw):
        if d.startswith('_'):
            continue
        func_name = _camelToSnake(d.replace('glfw', ''))
        try:
            func = getattr(_glfw, d)  # TODO: why doesn't this work on ubuntu?
        except AttributeError:
            continue
        if hasattr(func, '__call__'):
            funcs[func_name] = func
            camelCase[d] = func
    # TODO: This elegance should not die...
    # funcs = {
    #     _camelToSnake(d.replace('glfw', '')): getattr(_glfw, d)
    #     for d in dir(_glfw)
    #     if not d.startswith('_')
    #     if hasattr(getattr(_glfw, d), '__call__')
    # }

    # Auto-wrap functions to make the friendly to Python
    for line in source.split('\n'):
        func_decl = _get_function_declaration(line)
        if func_decl:
            snake_name = func_decl['snake_name']
            if snake_name in funcs:
                some_func = funcs[snake_name]
                funcs[snake_name] = _wrap_func(ffi, func_decl, some_func)
            else:
                decl_func_name = func_decl['func_name']
                try:
                    func = getattr(_glfw, decl_func_name, None)
                except AttributeError:
                    continue
                if func:
                    funcs[snake_name] = _wrap_func(ffi, func_decl, func)
                    camelCase[decl_func_name] = func

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
    camelCase = {}


    # TODO: Make this work
    # camelCase = {
    #     d: getattr(_glfw, d)
    #     for d in dir(_glfw)
    # }

    # Segregate python from cffi
    core = imp.new_module('core')
    sys.modules['{}.core'.format(modname)] = core
    core.__dict__.update(camelCase)

    # Add standard API to module.  Note the lack of wrapping
    globals()['core'] = core

    # Update decorators
    decorators = imp.new_module('decorators')
    sys.modules['{}.decorators'.format(modname)] = decorators
    decorators.__dict__.update(
        dict(
            char_callback=ffi.callback('void (GLFWwindow*, unsigned int)'),
            cursor_enter_callback=ffi.callback('void (GLFWwindow*, int)'),
            cursor_pos_callback=ffi.callback('void (GLFWwindow*, double, double)'),
            error_callback=ffi.callback('void (int, const char*)'),
            frame_buffersize_callback=ffi.callback('void (GLFWwindow*, int, int)'),
            key_callback=ffi.callback('void (GLFWwindow*, int, int, int, int)'),
            monitor_callback=ffi.callback('void (GLFWmonitor*, int)'),
            mouse_button_callback=ffi.callback('void (GLFWwindow*, int, int, int)'),
            scroll_callback=ffi.callback('void (GLFWwindow*, double, double)'),
            window_close_callback=ffi.callback('void (GLFWwindow*)'),
            window_focus_callback=ffi.callback('void (GLFWwindow*, int)'),
            window_iconify_callback=ffi.callback('void (GLFWwindow*, int)'),
            window_pos_callback=ffi.callback('void (GLFWwindow*, int, int)'),
            window_refresh_callback=ffi.callback('void (GLFWwindow*)'),
            window_size_callback=ffi.callback('void (GLFWwindow*, int, int)'),
        )
    )

    # Add decorators module.  Note the lack of wrapping
    globals()['decorators'] = decorators
    return ffi, _glfw

# Cleanup namespace
_ffi, _glfw = _initialize_module(FFI())
globs = {k: v for k, v in globals().items()}
for func in globs:
    if func not in ['_ffi', '_glfw']:
        if (func.startswith('_') and not func.startswith('__')) or func in ['modname']:
            globals().pop(func)
globals().pop('globs')
globals().pop('func')


###############################################################################
# Hand written functions
###############################################################################
def create_window(width=640, height=480, title="Untitled", monitor=None, context=None):
    '''Creates a window

    Context is used when state from one window needs to be transferred
    to the new window.  A GlfwWindow * can be used for context.
    This is common when switching between full-screen and windowed
    mode.  During this operation, the window must be destroyed and
    re-created.
    '''
    if monitor is None:
        monitor = _ffi.NULL
    if context is None:
        context = _ffi.NULL
    args = (width, height, title, monitor, context)
    win = _glfw.glfwCreateWindow(*args)
    return win


###############################################################################
# Special error handler callback
###############################################################################
_error_callback_wrapper = None


def set_error_callback(func):
    @decorators.error_callback
    def wrapper(error, description):
        return func(error, _ffi.string(description))
    global _error_callback_wrapper
    _error_callback_wrapper = wrapper
    _glfw.glfwSetErrorCallback(wrapper)


###############################################################################
# Special helper functions
###############################################################################
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
    return {v: k.lower() for k, v in globals().items() if k in options}.get(action, action)
