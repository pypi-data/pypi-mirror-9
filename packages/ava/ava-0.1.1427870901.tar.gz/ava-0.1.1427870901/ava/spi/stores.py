# -*- coding: utf-8 -*-
"""
Data stores
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .context import instance

_dataengine = instance().get('dataengine')


def names():
    return _dataengine.store_names()


def create(store_name):
    return _dataengine.create_store(store_name)


def remove(store_name):
    return _dataengine.remove_store(store_name)


def get(store_name):
    return _dataengine.get_store(store_name)