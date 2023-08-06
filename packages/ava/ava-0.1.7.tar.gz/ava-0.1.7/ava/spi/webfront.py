# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

"""
Imports utility functions from Bottle for exposing web resource.
"""
import os
from ava.runtime import environ

from bottle import route, get, post, delete, put, request, response
from bottle import static_file as _static_file
from ava.core.webfront import dispatcher

static_folder = os.path.join(environ.pod_dir(), 'static')


def static_file(filepath, root=static_folder, mimetype='auto', download=False, charset='utf-8'):
    return _static_file(filepath, root=root, mimetype=mimetype, download=download, charset=charset)


def swap_root_app(wsgiapp):
    """ Swap the root WSGI application.

    :param wsgiapp:
    :return: the previous WSGI application.
    """
    from ava.core.webfront import dispatcher
    old_app = dispatcher.app
    dispatcher.app = wsgiapp

    return old_app

__all__ = [route, get, post, delete, put, request, response,
           static_file, static_folder, dispatcher, ]

