GLFW-CFFI
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

## Contributions:

I welcome pull requests for patches, but I have limited time so I may
be slow in responding immediately.

