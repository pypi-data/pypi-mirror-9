# -*- coding: utf-8 -*-
"""
For serving static content in webroot folder.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from ava.spi.webfront import route, static_file


@route('/')
@route('/<filepath:path>')
def serve_static(filepath='index.html'):
    return static_file(filepath)

