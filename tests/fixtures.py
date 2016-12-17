# -*- coding: utf-8 -*-
import pytest


def setup_window(major, minor):
    import glfw
    from glfw import gl
    glfw.init()

    version = (major, minor)
    glfw.window_hint(glfw.FOCUSED, False)
    glfw.window_hint(glfw.SAMPLES, 4)
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, major)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, minor)
    # Setup profile if less than opengl 3.2
    profile = glfw.OPENGL_ANY_PROFILE if version < (3, 2) else glfw.OPENGL_CORE_PROFILE
    glfw.window_hint(glfw.OPENGL_PROFILE, profile)
    # Setup forward compatibility if able
    forward_compat = gl.GL_FALSE if version < (3, 0) else gl.GL_TRUE
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, forward_compat)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)
    glfw.window_hint(glfw.OPENGL_FORWARD_COMPAT, True)
    glfw.window_hint(glfw.RED_BITS, 24)
    glfw.window_hint(glfw.GREEN_BITS, 24)
    glfw.window_hint(glfw.BLUE_BITS, 24)
    glfw.window_hint(glfw.ALPHA_BITS, 24)
    glfw.window_hint(glfw.DEPTH_BITS, 24)


@pytest.fixture(scope="function")
def setup_glfw():
    import glfw
    assert glfw.init()


@pytest.fixture(scope='function')
def primary_monitor():
    import glfw
    glfw.init()
    handle = glfw.core.glfwGetPrimaryMonitor()
    mon = glfw.Monitor(handle)
    return mon


@pytest.mark.usefixtures("setup_glfw")
@pytest.fixture(scope="function")
def opengl_version():
    import glfw
    from glfw import ffi, gl

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
        except Exception:
            opengl_version = None
    if opengl_version is None:
        raise RuntimeError('OpenGL context could not be generated.')
    return opengl_version


@pytest.fixture(scope="function")
def window(opengl_version):
    import glfw

    major, minor = opengl_version
    setup_window(major, minor)

    title = 'Test Fixture Window'
    width = 1
    height = 1
    win = glfw.create_window(title=title, width=width, height=height)
    glfw.core.make_context_current(win)
    return win


@pytest.mark.usefixtures("setup_glfw")
@pytest.fixture(scope='function')
def opengl_info(opengl_version, window):
    import glfw
    from glfw import gl

    glfw.make_context_current(window)
    opengl_info = {
        'glfw': glfw.get_version_string(),
        'version': gl.get_string(gl.VERSION),
        'vendor': gl.get_string(gl.VENDOR),
        'renderer': gl.get_string(gl.RENDERER),
        'GLSL': gl.get_string(gl.SHADING_LANGUAGE_VERSION),
    }
    # glfw.terminate()
    opengl_info = {k: str(v) for k, v in opengl_info.items()}
    return opengl_info


@pytest.fixture(scope="function")
def fullscreen(opengl_version):
    import glfw

    major, minor = opengl_version
    setup_window(major, minor)

    title = 'Test Fixture Fullscreen'
    handle = glfw.get_primary_monitor()
    monitor = glfw.Monitor(handle)
    # Use the monitor's window so that it doesn't reset all other monitors
    # This actually reduces test time.
    width, height = monitor.width, monitor.height
    win = glfw.create_window(title=title, width=width, height=height, monitor='primary')
    glfw.core.make_context_current(win)
    return win


@pytest.fixture(scope="function")
def windowed_fullscreen(opengl_version):
    import glfw

    major, minor = opengl_version
    setup_window(major, minor)

    title = 'Test Fixture Windowed Fullscreen'
    monitor = glfw.get_primary_monitor()
    mode = glfw.get_video_mode(monitor)
    # Use the monitor's window so that it doesn't reset all other monitors
    # This actually reduces test time.
    width, height = mode.width, mode.height
    win = glfw.create_window(title=title, width=width, height=height, monitor=0)
    glfw.core.make_context_current(win)
    return win
