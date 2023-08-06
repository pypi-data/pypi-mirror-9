# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import unittest
import gevent
from ava.core.agent import Agent


class AgentTest(unittest.TestCase):
    """
    For functional/integration tests which require a running agent.
    """
    agent = None

    @classmethod
    def setUpClass(cls):
        AgentTest.agent = Agent()
        agent_greenlet = gevent.spawn(AgentTest.agent.run)

    @classmethod
    def tearDownClass(cls):
        AgentTest.agent.interrupted = True
        while AgentTest.agent.running:
            gevent.sleep(0.5)
