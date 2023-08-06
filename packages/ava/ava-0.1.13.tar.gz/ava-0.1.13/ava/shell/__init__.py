# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys


# helper function for constructing paths to resource files.
def resource_path(relative):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative)

    res_path = os.environ.get("RESOURCEPATH", None)
    if res_path is None:
        abspath = os.path.abspath(os.path.join(__file__, "..", ".."))
        abspath = os.path.dirname(abspath)
        #print("abspath: ", abspath)
        return os.path.join(abspath, relative)
    else:
        return os.path.join(res_path, relative)



