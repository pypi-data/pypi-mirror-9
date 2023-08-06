# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
"""
Commands for controlling the agent process.
"""

import sys
import gevent
from ava.spi.webfront import post


def _restart():
    """
    Tells shell to restart the agent process.
    """
    sys.exit(1)


@post("/api/agent/restart")
def restart():
    gevent.spawn_later(3, _restart)
    return "Ava is restarting..."



