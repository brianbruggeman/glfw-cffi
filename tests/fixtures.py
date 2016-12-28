# -*- coding: utf-8 -*-
import pytest


def setup_window(major, minor):
    import glfw
    from glfw import gl
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

    version = (major, minor)
    glfw.window_hint(glfw.FOCUSED, False)
    glfw.window_hint(glfw.VISIBLE, False)
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


@pytest.fixture(scope='function')
def primary_monitor():
    import glfw
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

    handle = glfw.core.glfwGetPrimaryMonitor()
    mon = glfw.Monitor(handle)
    return mon


@pytest.fixture(scope="function")
def opengl_version(primary_monitor):
    import glfw
    from glfw import ffi
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

    win = glfw.create_window()
    print('GL Version: {}'.format(glfw.gl.get_string(glfw.gl.VERSION)))
    default = (
        glfw.gl.get_integerv(glfw.gl.MAJOR_VERSION),
        glfw.gl.get_integerv(glfw.gl.MINOR_VERSION)
    )
    print('getIntegerV(Major,Minor): {}'.format(default))

    opengl_version = default
    versions = [
        (4, 5), (4, 4), (4, 3), (4, 2), (4, 1), (4, 0),
        (3, 3), (3, 2), (3, 1), (3, 0),
        (2, 1), (2, 0),
        (1, 5), (1, 4), (1, 3), (1, 2), (1, 1), (1, 0),
    ]
    title = 'opengl version finder'
    width, height = primary_monitor.width, primary_monitor.height

    if not glfw.core.init():
        glfw.terminate()
        raise RuntimeError('Could not initialize GLFW')

    for major, minor in versions:
        try:
            setup_window(major, minor)
            window = glfw.create_window(width=width, height=height, title=title, monitor=primary_monitor)
            if window != ffi.NULL:
                glfw.destroy_window(window)
                if opengl_version in set((None, (0, 0), default)):
                    opengl_version = (major, minor)
                    break
            elif 0:
                emsg = 'Could not create context using GL version: {major}.{minor}'
                print(emsg.format(major=major, minor=minor))
        except Exception as e:
            import traceback
            print(traceback.format_exc())
            opengl_version = None
    if opengl_version is None:
        raise RuntimeError('OpenGL context could not be generated.')
    return opengl_version


@pytest.fixture(scope="function")
def window(primary_monitor, opengl_version):
    import glfw
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

    major, minor = opengl_version
    setup_window(major, minor)

    title = 'Test Fixture Window'
    width = primary_monitor.width
    height = primary_monitor.height
    win = glfw.create_window(title=title, width=width, height=height)
    glfw.core.make_context_current(win)
    return win


@pytest.fixture(scope='function')
def opengl_info(opengl_version, window):
    import glfw
    from glfw import gl
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

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
def fullscreen(primary_monitor, opengl_version):
    import glfw
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

    major, minor = opengl_version
    setup_window(major, minor)

    title = 'Test Fixture Fullscreen'
    # Use the monitor's window so that it doesn't reset all other monitors
    # This actually reduces test time.
    width, height = primary_monitor.width, primary_monitor.height
    win = glfw.create_window(title=title, width=width, height=height, monitor='primary')
    glfw.core.make_context_current(win)
    return win


@pytest.fixture(scope="function")
def windowed_fullscreen(primary_monitor, opengl_version):
    import glfw
    glfw.init()
    assert glfw.init() == glfw.gl.TRUE

    major, minor = opengl_version
    setup_window(major, minor)

    title = 'Test Fixture Windowed Fullscreen'
    # Use the monitor's window so that it doesn't reset all other monitors
    # This actually reduces test time.
    width, height = primary_monitor.width, primary_monitor.height
    win = glfw.create_window(title=title, width=width, height=height, monitor=0)
    glfw.core.make_context_current(win)
    return win
