# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

from .webfront import dispatcher
from ws4py.websocket import EchoWebSocket
from ws4py.server.wsgiutils import WebSocketWSGIApplication


class WebSocketHandler(EchoWebSocket):
    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)


class WebsocketEngine(object):
    def start(self, ctx=None):
        dispatcher.mount('/ws', WebSocketWSGIApplication(
            handler_cls=WebSocketHandler))

    def stop(self, ctx=None):
        pass