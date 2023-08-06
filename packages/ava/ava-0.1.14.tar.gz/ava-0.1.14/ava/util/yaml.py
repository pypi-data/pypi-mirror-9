# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from yaml import load as _load, dump as _dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


def load(stream):
    return _load(stream, Loader=Loader)


def dump(data, stream, **options):
    return _dump(data,
                 stream,
                 Dumper=Dumper,
                 default_flow_style=False,
                 indent=4, width=80,
                 **options)