# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import unittest

from ava.spi.context import Context


class Receiver(object):
    def __init__(self):
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True


class CoreContextTest(unittest.TestCase):

    def setUp(self):
        self.context = Context(None)

    def test_send_signal(self):
        SIGNAL = 'my-first-signal'

        receiver = Receiver()
        self.context.connect(receiver, signal=SIGNAL)
        self.context.send(signal=SIGNAL)
        self.assertTrue(receiver.called)

    def test_connect_and_then_disconnect(self):
        SIGNAL = 'my-second-signal'
        receiver = Receiver()
        self.context.connect(receiver)
        self.context.send(signal=SIGNAL)
        self.assertTrue(receiver.called)
        receiver.called = False
        self.context.disconnect(receiver)
        self.context.send(signal=SIGNAL)
        self.assertFalse(receiver.called)