# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import unittest

from ava.spi import signals


class Receiver(object):
    def __init__(self):
        self.called = False

    def __call__(self, *args, **kwargs):
        self.called = True


class SignalsTest(unittest.TestCase):

    def test_send_signal(self):
        SIGNAL = 'my-first-signal'

        receiver = Receiver()
        signals.connect(receiver, signal=SIGNAL)
        signals.send(signal=SIGNAL)
        self.assertTrue(receiver.called)

    def test_connect_and_then_disconnect(self):
        SIGNAL = 'my-second-signal'
        receiver = Receiver()
        signals.connect(receiver)
        signals.send(signal=SIGNAL)
        self.assertTrue(receiver.called)
        receiver.called = False
        signals.disconnect(receiver)
        signals.send(signal=SIGNAL)
        self.assertFalse(receiver.called)