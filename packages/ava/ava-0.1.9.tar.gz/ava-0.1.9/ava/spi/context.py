# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from pydispatch import dispatcher


class Context(object):
    """
    The top context for all other entities.
    """
    def __init__(self, agent):
        self._agent = agent
        self._attributes = {}
        self._dispatcher = dispatcher

    def __getitem__(self, item):
        return self.get(item)

    def __setitem__(self, key, value):
        self.bind(key, value)

    def __delitem__(self, key):
        self.unbind(key)

    def __getattr__(self, item):
        return self.get(item)

    def bind(self, key, provider):
        self._attributes[key] = provider

    def unbind(self, key):
        del self._attributes[key]

    def get(self, key, default=None):
        obj = self._attributes.get(key)
        if not obj:
            return default
        elif callable(obj):
            return obj()
        else:
            return obj

    def add_child_greenlet(self, child):
        self._agent.add_child_greenlet(child)

    def send(self, *args, **kwargs):
        """
        Send signal/event to registered receivers.

        :param args:
        :param kwargs:
        :return:
        """
        self._dispatcher.send(*args, **kwargs)

    def connect(self, receiver, *args, **kwargs):
        """
        Connect the receiver to listen for signals/events.
        :param signal:
        :param sender:
        :return:
        """
        self._dispatcher.connect(receiver, *args, **kwargs)

    def disconnect(self, receiver, *args, **kwargs):
        """
        Disconnect the specified receiver.
        :return:
        """
        self._dispatcher.disconnect(receiver, *args, **kwargs)


class Component(object):
    """
    Base for component classes.
    """
    pass


####  Singleton construction  ####
_context = None


def instance(agent=None):
    """
    Gets the context singleton. Must first be invoked by agent.

    :param agent:
    :return:
    """
    global _context
    if _context is None:
        _context = Context(agent)

    return _context
