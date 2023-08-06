# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


def create():
    """
    Creates the shell based on a specified platform.

    :param platform: The platform identifier.
    :return:
    """
    from ava.shell.console import Shell

    return Shell()