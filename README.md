GLFW-CFFI
---------
[![Build Status](https://travis-ci.org/brianbruggeman/glfw-cffi.svg)](https://travis-ci.org/brianbruggeman/glfw-cffi)
[![PyPI version](https://badge.fury.io/py/glfw-cffi.svg)](https://pypi.python.org/pypi/glfw-cffi)

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
- Windows: There is an installer available
  [64-bit Windows](https://github.com/glfw/glfw/releases/download/3.1.2/glfw-3.1.2.bin.WIN64.zip) or
  [32-bit Windows](https://github.com/glfw/glfw/releases/download/3.1.2/glfw-3.1.2.bin.WIN32.zip)

## Usage:

Please note that the convention for Python is to use snake_case and not
to duplicate API references (e.g. GLFW_<SOME_DEFINE> or glfwSomeCamelCaseFunction).  Instead, where you may have used:

       #define GLFW_REFRESH_RATE

You may now use in Python:

       import glfw
       ...
       glfw.REFRESH_RATE

Where you may have used:

       glfwInit();

In Python, you can use:

       import glfw
       ...
       glfw.init()

Additionally, I have added keywords based on the header information.
For example, a simple program to open a window might look like:

       import glfw
       ...
       win = glfw.create_window(width=640, height=480, title='Hello, World!')

I have added the function signatures from the header code into the
docstrings for the functions.  This should provide at least some help
when trying to write a program for the first time using this library.

If you happen to feel like you miss the old style found directly within
the c-code, you may use them as follows.  This should help with porting
old code directly into cffi or following the numerous examples within
the GLFW docs:

        from glfw.core import *

        glfwInit()
        glfwCreateWindow(640, 480, 'Hello, World!')
        ...
        glfwTerminate()

## Examples:

More examples can be within the github repo under the [examples/](https://github.com/brianbruggeman/glfw-cffi/tree/develop/examples) folder.


## Contributions:

I welcome pull requests for patches, but I have limited time so I may
be slow in responding immediately.

