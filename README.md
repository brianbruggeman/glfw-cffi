GLFW-CFFI
---------
[![Build Status](https://travis-ci.org/brianbruggeman/glfw-cffi.svg)](https://travis-ci.org/brianbruggeman/glfw-cffi)
[![PyPI version](https://img.shields.io/pypi/v/glfw-cffi.svg)](https://pypi.python.org/pypi/glfw-cffi)
[![Status](https://img.shields.io/pypi/status/glfw-cffi.svg)](https://pypi.python.org/pypi/glfw-cffi)
[![Python Compatibility](https://img.shields.io/pypi/pyversions/glfw-cffi.svg)](https://pypi.python.org/pypi/glfw-cffi)
[![Downloads](https://img.shields.io/pypi/dm/glfw-cffi.svg?period=week)](https://pypi.python.org/pypi/glfw-cffi)
[![Coverage Status](https://coveralls.io/repos/brianbruggeman/glfw-cffi/badge.svg?branch=develop&service=github)](https://coveralls.io/github/brianbruggeman/glfw-cffi?branch=develop)

A wrapper for GLFW3 using Python's CFFI.

## Motivation:

After being frustrated with the options available, I decided to roll my
own version of glfw3 using cffi for python.  This package inspects the
header file for glfw's api, and then creates python-wrapped functions.

For the most part, this should be transparent.  However, I have not
tested the package well enough to know where the bugs are.  So you may
use at your own risk.

Additionally, I have provided a straight copy of the GLFW3 api directly
available from the module.  So the module has python friendly functions
as well as the direct C-library calls.  Note that the latter API requires
more setup to use because you must manage the object conversion from
Python into C and back.

The goal for this package is that the user won't know they're using
a C library underneath and the package interface will feel completely
natural within Python.

## License:

This package is released as Apache 2.0 license.

However, at your option, you may apply any OSI approved free software
license you choose provided that you adhere to the free software license
chosen and additionally follow these criteria:

 a. list the author's name of this software as a contributor to your
    final product

 b. provide credit to your end user of your product or software without
    your end user asking for where you obtained your software

 c. notify the author of this software that you are using this software

 d. If you believe there can be some benefit in providing your changes
    upstream, you'll submit a change request.  While this criteria is
    completely optional, please consider not being a dick.

## Installation:

GLFW-CFFI uses GLFW3 and attempts to find the header file associated with your
specific library version to autogenerate the FFI interface.  So a version of
GLFW3 must be available during installation.  If a development version is
unavailable, then a version of the `glfw3.h` is included within the `glfw-cffi`
package itself.

### Installing via pip

Install via `pip install glfw-cffi`.

### Installing GLFW3

GLFW3 is available for several different platforms:

- Ubuntu/Debian: `sudo apt-get install -y libglfw3-dev`
- Fedora/Red Hat: `sudo yum install -y libglfw3-dev`
- Mac OS X with Homebrew: `brew install glfw3`
- Windows: There is are pre-compiled binaries available
  [64-bit Windows](https://github.com/glfw/glfw/releases/download/3.1.2/glfw-3.1.2.bin.WIN64.zip) or
  [32-bit Windows](https://github.com/glfw/glfw/releases/download/3.1.2/glfw-3.1.2.bin.WIN32.zip)

GLFW3 is relatively new, so some older installations of Linux may not have
`libglfw` directly available.  You may check out the [travis.yml](https://github.com/brianbruggeman/glfw-cffi/blob/master/.travis.yml#L34-L52)
file within our github repo for more information on setup on older systems.

#### A special note for installing GLFW3 on Windows

The current state requires that an environment variable, 'GLFW_LIBRARY', be set
and pointing to a compiled .dll found within a known path.  In addition,
glfw-cffi expects that a header file be present within an 'include' folder
within the same folder structure as the .dll.  So for example, if the
library binary were added to:

    C:\GLFW\lib\glfw3.dll

The python library, glfw-cffi, would search for a glfw3.h file within any of
these folders:

    C:\GLFW\lib\include
    C:\GLFW\include
    C:\include

When testing, we used the 32-bit binary and lib-mingw on a 64-bit Windows 10
system.

## Usage:

### Sample Usage:

This is the required code to produce a window on the screen:

    import glfw

    # Initialize glfw
    if not glfw.init():
        glfw.terminate()  # Cleans up if necessary
        raise RuntimeError('Could not initialize GLFW3')

    # Create window and set OpenGL Context
    win = glfw.create_window(title='Simple Window', width=640, height=480)
    glfw.make_context_current(win)

    # Main Loop
    while not glfw.window_should_close(win):
        glfw.swap_buffers(win)
        # To handle/process events use:
        glfw.poll_events()  # for continuous rendering (like in games)
        # or use:
        # glfw.wait_events()  # for on-event UIs (like an editing tool)

    # Proper shutdown
    glfw.terminate()

A more complex window example can be found within the examples folder on the github repo.

### Decorators

Extra decorators have been added to aid with developing a full user interface, including:

- keyboard handling
- mouse handling
- joystick handling
- window events
- text events
- path drop callbacks  (for drag and drop)
- error callbacks

Each decorator may be used with a standalone function or decorating a class method.
Examples of each type are found in the subsections below.  When decorating a class
method, use: @[staticmethod](https://docs.python.org/2/library/functions.html#staticmethod).

What follows is only the more commonly used.  Better documentation on callbacks can
be found on the [glfw website](http://www.glfw.org/docs/latest/).

#### Handling keyboard events

Keyboard events have a single decorator:

- keyboard event:  glfw.decorators.key_callback

Example:

    import glfw

    @glfw.decorators.key_callback
    def on_key(win, key, code, action, mods):
        '''Converts key into an event'''
        if key in [glfw.KEY_ESCAPE] and action in [glfw.PRESS]:
            glfw.set_window_should_close(win, gl.GL_TRUE)


In addition, helper functions have been added to convert data into strings:


    def display_data(key, action, mods):
        '''Converts keystroke into string data'''
        # Convert data
        key_action = glfw.get_key_string(key)
        action_string = glfw.get_action_string(action)
        mods_string = glfw.get_mod_string(mods)
        # Display data
        print('key: {key} -> "{string}"'.format(key=key, string=key_string))
        print('action: {action} -> "{string}"'.format(action=action, string=action_string))
        print('mods: {mods} -> "{string}"'.format(mods=mods, string=mods_string))


Finally, sometimes keystroke handling may make sense to be included within a class.


    import glfw
    from OpenGL import GL as gl

    class Foo(object):

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
            print(string)


#### Handling mouse events

Mouse events have three decorators:

- mouse button click:  glfw.decorators.mouse_button_callback
- mouse wheel/scroll: glfw.decorators.scroll_callback
- mouse movement: glfw.decorators.cursor_pos_callback

Example:

    import glfw
    from OpenGL import GL as gl


    class Foo(object):

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
            print(string)

        @staticmethod
        @glfw.decorators.scroll_callback
        def on_mouse_scroll(win, x_offset, y_offset):
            '''Handles a mouse scroll/wheel event'''

        @staticmethod
        @glfw.decorators.cursor_pos_callback
        def on_mouse_move(win, x_offset, y_offset):
            '''Handles a mouse move event'''



#### Handling window events

There are other available decorators that handle window events.

##### Gaining and Losing Focus

Windows client areas may gain or lose focus and an event is
triggered each time.

- client focus: glfw.decorators.cursor_enter_callback
- window focus: glfw.decorators.window_focus_callback

Example:

    import glfw


    class Foo(object):

        @staticmethod
        @glfw.decorators.cursor_enter_callback
        def on_enter(win, status):
          '''Handles focus event for a window client area

          status is a boolean:  True for focused and False for unfocused
          '''

        @staticmethod
        @glfw.decorators.window_focus_callback
        def on_enter(win, status):
          '''Handles focus event for a window

          status is a boolean:  True for focused and False for unfocused
          '''

##### Resizing

Windows may be resized.

- resize: glfw.decorators.window_size_callback

Example:

    import glfw


    class Foo(object):

        @staticmethod
        @glfw.decorators.window_size_callback
        def on_enter(win, width, height):
          '''Handles resize event'''


## Examples:

More examples can be within the github repo under the [examples/](https://github.com/brianbruggeman/glfw-cffi/tree/develop/examples) folder.

Some of the examples require more packages to be installed:

- [docopt](https://pypi.python.org/pypi/docopt):  Creates beautiful command-line interfaces
- [numpy](https://pypi.python.org/pypi/numpy):  is a general-purpose array-processing package designed to efficiently manipulate large multi-dimensional arrays of arbitrary records without sacrificing too much speed for small multi-dimensional arrays
- [freetype-py](https://pypi.python.org/pypi/freetype-py/): Freetype python provides bindings for the FreeType library. Only the high-level API is bound.


## Contributions:

Contributions are welcome. When opening a PR, please keep the following guidelines in mind:

- Before implementing, please open an issue for discussion.
- Make sure you have tests for the new logic.
- Make sure your code passes `flake8`
- Add yourself to contributors at `README.md` and/or  your contributions.

## Contributors

* [Brian Bruggeman](https://github.com/brianbruggeman) - Originator
