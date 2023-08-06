# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

from ava.spi.webfront import route, static_file


@route('/')
@route('/index.html')
def serve_root():
    return static_file(b'index.html')


@route('/favicon.ico')
def serve_favicon():
    return static_file(b'eavatar.ico')


@route('/static/<filepath:path>')
def serve_static(filepath):
    return static_file(filepath)

