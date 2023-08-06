# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
"""
Commands for controlling the agent process.
"""

import sys
import gevent
import bottle
from ava.spi.webfront import dispatcher, check_authentication

api = dispatcher.mount(b'agent', bottle.Bottle())
api.add_hook('before_request', check_authentication)


def _restart():
    """
    Tells shell to restart the agent process.
    """
    sys.exit(1)


@api.post("/restart")
def restart():
    gevent.spawn_later(3, _restart)
    return "Agent is restarting..."


@api.get("/status")
def status():
    return "Agent is running..."


