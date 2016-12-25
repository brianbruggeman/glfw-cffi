#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import print_function, division

from pprint import pprint as pp

import pytest


@pytest.mark.unit
def test_import():
    '''Basic test to determine if glfw can be imported successfully'''
    import glfw
    assert locals()['glfw'] == glfw


@pytest.mark.unit
def test_pre_init():
    '''Tests functions from glfw core that can be run prior to running
    init (also including init)'''
    import glfw

    @glfw.decorators.error_callback
    def error_callback(error, description):
        pass

    # These can be called before init
    assert glfw.set_error_callback(error_callback) is None
    glfw_version = glfw.get_version()
    glfw_version_string = glfw.get_version_string()
    assert glfw_version is not None
    assert glfw_version_string.startswith(bytes('.'.join('{}'.format(v) for v in glfw_version).encode('utf-8')))
    assert glfw.init() != 0
    assert glfw.terminate() is None


@pytest.mark.unit
def test_basic_package_functions():
    '''Runs tests on basic package information that is available to the
    end user
    '''
    import glfw
    assert glfw.get_include() is not None
    assert glfw.get_key_string(glfw.KEY_A) == 'a'
    assert glfw.get_mod_string(glfw.MOD_SHIFT) == 'shift'
    assert glfw.get_mouse_button_string(glfw.MOUSE_BUTTON_LEFT) == 'left'
    assert glfw.get_action_string(glfw.RELEASE) == 'release'


@pytest.mark.unit
def test_basic_window(window):
    '''Runs a simple window example'''
    import glfw
    assert window != glfw.ffi.NULL
    for x in range(2):
        assert glfw.swap_buffers(window) is None
        assert glfw.poll_events() is None
    assert window is not None
    assert glfw.terminate() is None


@pytest.mark.unit
def test_basic_fullscreen(fullscreen):
    '''Runs a simple window example'''
    import glfw
    assert fullscreen != glfw.ffi.NULL
    for x in range(2):
        assert glfw.swap_buffers(fullscreen) is None
        assert glfw.poll_events() is None
    assert fullscreen is not None
    assert glfw.terminate() is None


@pytest.mark.unit
def test_basic_windowed_fullscreen(windowed_fullscreen):
    '''Runs a simple window example'''
    import glfw
    assert windowed_fullscreen != glfw.ffi.NULL
    for x in range(2):
        assert glfw.swap_buffers(windowed_fullscreen) is None
        assert glfw.poll_events() is None
    assert windowed_fullscreen is not None
    assert glfw.terminate() is None


@pytest.mark.unit
def test_opengl_compatibility(opengl_version, opengl_info):
    import glfw

    if 'extensions' in opengl_info:
        for extension in opengl_info.get('extensions'):
            pp('OpenGL Extension: {}'.format(extension))
    if 'glsl_supported' in opengl_info:
        for glsl in opengl_info.get('extensions'):
            if glsl != opengl_info['GLSL']:
                pp('OpenGL GLSL Supported: {}'.format(glsl))
    assert glfw.terminate() is None
    version_string = '.'.join(map(str, opengl_version))
    assert version_string in opengl_info['version']


@pytest.mark.unit
def test_basic_monitor(primary_monitor):
    import glfw
    glfw.init()

    mon = glfw.get_primary_monitor()
    assert mon == primary_monitor.handle

    modes = glfw.get_video_mode(mon)
    size = glfw.get_monitor_physical_size(mon)
    res = modes.width, modes.height
    name = glfw.get_monitor_name(mon)
    assert primary_monitor.position == (0, 0)
    assert primary_monitor.connected is True
    assert tuple(primary_monitor.size) == tuple(size)
    assert primary_monitor.height, primary_monitor.width == res
    assert primary_monitor.resolution == res
    assert primary_monitor.rotated is False
    assert primary_monitor.name == name
    assert primary_monitor.primary is True


@pytest.mark.unit
def test_multi_monitor_create_window():
    import glfw
    glfw.init()

    monitors = glfw.get_monitors()
    last_monitor = monitors[-1]

    window = glfw.create_window(
        width=last_monitor.width,
        height=last_monitor.height,
        title='Multi-monitor test',
        monitor=last_monitor)


@pytest.mark.unit
def test_create_window_exception():
    import glfw
    glfw.init()

    with pytest.raises(RuntimeError):
        glfw.terminate()

        window = glfw.create_window(title='Window Exception test')


@pytest.mark.unit
def test_api_monitor():
    import glfw
    glfw.init()

    mon = glfw.Monitor()


@pytest.mark.unit
def test_ffi_string():
    import glfw
    glfw.init()

    test_string = b'hello, world'
    my_string = glfw.ffi.new('char[]', test_string)
    assert glfw.ffi_string(my_string) == test_string


if __name__ == '__main__':
    pytest.main()
