# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
from gevent import monkey
monkey.patch_all()

import unittest
import gevent
import ws4py
from ws4py.client.geventclient import WebSocketClient


class WebsocketTest(unittest.TestCase):

    def test_websocket_connection(self):
        ws = WebSocketClient('ws://127.0.0.1:5080/ws')
        ws.connect()
        print("Sending: 'Hello, World'...")
        ws.send("Hello, World")
        print("Sent")
        print("Receiving...")
        result = ws.receive()
        print("Received: {}".format(result))
        ws.close()
        self.assertEqual("Hello, World", str(result))

    def test_secure_websocket_connection(self):
        ws = WebSocketClient('wss://127.0.0.1:5443/ws')
        ws.connect()
        print("Sending: 'Hello, World'...")
        ws.send("Hello, World")
        print("Sent")
        print("Receiving...")
        result = ws.receive()
        print("Received: {}".format(result))
        ws.close()
        self.assertEqual("Hello, World", str(result))