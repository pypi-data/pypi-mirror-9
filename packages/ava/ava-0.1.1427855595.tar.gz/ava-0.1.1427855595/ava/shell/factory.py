# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

def create():
    """
    Creates the shell based on a specified platform.

    :param platform: The platform identifier.
    :return:
    """
    plat = sys.platform
    if plat.startswith("win32"):
        from ava.shell.win32 import Shell
    elif plat.startswith("darwin"):
        from ava.shell.osx import Shell
    elif plat.startswith("linux"):
        from ava.shell.gtk import Shell
    else:
        from ava.shell.console import Shell

    return Shell()