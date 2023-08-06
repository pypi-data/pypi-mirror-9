# -*- coding: utf-8 -*-
"""
Various definitions used across different packages.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from ava import VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO, VERSION_STRING


# return as the root resource.
AGENT_INFO = {
    "EAvatar": "A versatile agent.",
    "version": VERSION_STRING,
    "vendor": {
        "name": "EAvatar Technology Ltd.",
        "version": "0.1.0"
    },
}


# activated engines

INSTALLED_ENGINES = [
    "ava.core.webfront:WebfrontEngine",
    "ava.core.task:TaskEngine",
    "ava.core.extension:ExtensionEngine",
    "ava.core.mod_tasks:TaskModEngine",
    "ava.core.mod_webhooks:WebhooksEngine",
#    "ava.core.websocket:WebsocketEngine",
]


##### Environment variable ####
AVA_POD_FOLDER = 'AVA_POD'  # where the working directory.
AVA_AGENT_SECRET = 'AVA_AGENT_SECRET'  # secret key for this agent.
AVA_USER_XID = 'AVA_USER_XID'  # the owner's public key.


# tries to import definitions from the global settings.

try:
    from settings import *
except ImportError:
    pass