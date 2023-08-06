# -*- coding: utf-8 -*-
"""
    Logging management.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import logging


def basicConfig(*args, **kwargs):
    logging.basicConfig(*args, **kwargs)


def getLogger(name):
    return logging.getLogger(name)

