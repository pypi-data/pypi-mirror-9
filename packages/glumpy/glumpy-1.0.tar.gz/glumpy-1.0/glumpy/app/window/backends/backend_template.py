# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright (c) 2014, Nicolas P. Rougier
# Distributed under the (new) BSD License. See LICENSE.txt for more info.
# -----------------------------------------------------------------------------
import os, sys
from glumpy import gl
from glumpy.log import log
from glumpy.app import configuration
from glumpy.app.window import window


# Backend name
__name__ = "Template"

# Backend version (if available)
__version__ = ""

# Backend availability
__availability__ = False

# Whether the framework has been initialized
__initialized__ = False

# Active windows
__windows__ = []


# ---------------------------------------------------- convenient functions ---
def name():      return __name__
def version():   return __version__
def available(): return __availability__


# --------------------------------------------------------------- init/exit ---
def __init__():
    global __initialized__
    __initialized__ = True

def __exit__():
    global __initialized__
    __initialized__ = False


# ------------------------------------------------------------ availability ---
try:
    import ToolKit # Replace with actual toolkit
    __availability__ = True
    __version__ = ""
    __key_map__   = { }
    __mouse_map__ = { }

except ImportError:
    __availability__ = False
    __version__ = None


# -------------------------------------------------------------- capability ---
capability = {
    "Window position get/set" : False,
    "Window size get/set"     : False,
    "Multiple windows"        : False,
    "Mouse scroll events"     : False,
    "Non-decorated window"    : False,
    "Non-sizeable window"     : False,
    "Fullscreen mode"         : False,
    "Unicode processing"      : False,
    "Set GL version"          : False,
    "Set GL profile"          : False,
    "Share GL context"        : False,
}



# ------------------------------------------------------- set_configuration ---
def set_configuration(configuration):
    # Put GL initialization here (depth buffer size, etc.)
    pass



# ------------------------------------------------------------------ Window ---
class Window(event.EventDispatcher):


    def __init__( self, width=512, height=512, title=None, visible=True, aspect=None,
                  decoration=True, fullscreen=False, config=None, context=None, color=(0,0,0,1)):

        window.Window.__init__(self, width=width,
                                     height=height,
                                     title=title,
                                     visible=visible,
                                     aspect=aspect,
                                     decoration=decoration,
                                     fullscreen=fullscreen,
                                     config=config,
                                     context=context,
                                     color=color)

        # Create the native window here
        # Each on the events below must be called at some point
        pass

        # self.dispatch_event('on_show')
        # self.dispatch_event('on_hide')
        # self.dispatch_event('on_close')
        # self.dispatch_event('on_resize', width, height)

        # self.dispatch_event('on_mouse_release', x, y, button)
        # self.dispatch_event('on_mouse_press', x, y, button)
        # self.dispatch_event('on_mouse_motion', x, y, dx, dy)
        # self.dispatch_event('on_mouse_drag', x, y, dx, dy, button)
        # self.dispatch_event('on_mouse_scroll', x, y, xoffset, yoffset)
        # self.dispatch_event('on_key_press', symbol, modifiers)
        # self.dispatch_event('on_key_release', symbol, modifiers)
        # self.dispatch_event('on_character', u"%c" % character)



# ----------------------------------------------------------------- windows ---
def windows():
    return __windows__


# ----------------------------------------------------------------- process ---
def process(dt):

    # Poll for and process events
    # -> Add toolkit specific code here to process events
    # -> Must always exit

    for window in __windows__:
        # Make window active
        window.activate()

        # Clear window using window clear flags
        gl.glClear(window._clearflags)

        # Dispatch the main draw event
        window.dispatch_event('on_draw', dt)

        # Dispatch the idle event
        window.dispatch_event('on_idle', dt)

        # Swap buffers
        window.swap()

    return len(__windows__)
