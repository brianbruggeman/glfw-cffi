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
# The entire point of this library is to reduce maintenance, so an
# import * is preferred.
from .__metadata__ import *  # noqa
from .api import *  # noqa
