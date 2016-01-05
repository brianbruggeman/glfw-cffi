GLFW-CFFI [![Build Status](https://travis-ci.org/brianbruggeman/glfw-cffi.svg)](https://travis-ci.org/brianbruggeman/glfw-cffi)
---------

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

   python setup.py install

## Requirements:

This install requires that glfw3 be installed.

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

