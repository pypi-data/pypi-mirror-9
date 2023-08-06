# -*- coding: utf-8 -*-
"""
Misc. utility classes/functions.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys


# helper function for constructing paths to resource files.
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    abspath = os.path.abspath(os.path.join(__file__, "..", ".."))
    abspath = os.path.dirname(abspath)
    #print("abspath: ", abspath)
    return os.path.join(abspath, relative)


# helper function for constructing paths to resource files.
def base_path():
    if hasattr(sys, "_MEIPASS"):
        return sys._MEIPASS
    else:
        # assumes this file is located at src/eavatar/util/__init__.py
        abspath = os.path.abspath(os.path.join(__file__, "..", ".."))
        abspath = os.path.dirname(abspath)
        return abspath


def is_frozen():
    """ Checks if in frozen mode.
    :return:
    """
    return hasattr(sys, "frozen")

if __name__=='__main__':
    print(resource_path('test'))
