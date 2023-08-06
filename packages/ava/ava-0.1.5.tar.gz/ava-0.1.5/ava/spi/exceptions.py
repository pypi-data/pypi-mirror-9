# -*- coding: utf-8 -*-
"""
Exceptions raised in eavtar.kits package.
"""
from __future__ import absolute_import, division, print_function, unicode_literals


class AvaError(Exception):
    """
    Raised when error is framework-related but no specific error subclass exists.
    """
    def __init__(self, *args, **kwargs):
        super(AvaError, self).__init__(args, kwargs)


class DataError(AvaError):
    """
    Generic error related to database operations.
    """
    pass


