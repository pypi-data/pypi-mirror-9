# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
"""
Intended to provide the definitions of significant signals.
"""

from pydispatch import dispatcher as _dispatcher

GREENLET_CREATED = 'greenlet.created'

AGENT_STARTED = "agent.started"
AGENT_STOPPING = "agent.stopping"

MODULE_LOADED = "module.loaded"
MODULE_UNLOADED = "module.unloaded"


def send(signal, *args, **kwargs):
    """
    Send signal/event to registered receivers.

    :param args:
    :param kwargs:
    :return:
    """
    _dispatcher.send(signal=signal, *args, **kwargs)


def connect(receiver, *args, **kwargs):
    """
    Connect the receiver to listen for signals/events.
    :param signal:
    :param sender:
    :return:
    """
    _dispatcher.connect(receiver, *args, **kwargs)


def disconnect(receiver, *args, **kwargs):
    """
    Disconnect the specified receiver.
    :return:
    """
    _dispatcher.disconnect(receiver, *args, **kwargs)

