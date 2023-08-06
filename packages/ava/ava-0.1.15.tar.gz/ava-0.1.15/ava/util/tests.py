# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import unittest
import gevent

from ava.spi.defines import AVA_USER_XID, AVA_AGENT_SECRET
from ava.runtime import settings
from ava.core.agent import Agent


class AgentTest(unittest.TestCase):
    """
    For functional tests which require a running agent.
    """
    agent = None
    user_xid = b'AYPwK3c3VK7ZdBvKfcbV5EmmCZ8zSb9viZ288gKFBFuE92jE'
    user_key = b'Kd2xqKsjTnhhqXjY64eeSEyS1i9kSGTHt9S57sqeK51bkPRh'
    user_secret = b'SVQh1mgbdvuFoZihYH8urZyBGpfZ4PJnn8af2R9MuqZyktHa'

    agent_secret = b'SYNmgyQqhAnVwKLrmSmYzahkzH3V51qdShL41JFPnmsZob96'

    @classmethod
    def setUpClass(cls):
        settings['debug'] = True
        os.environ.setdefault(AVA_USER_XID, cls.user_xid)
        os.environ.setdefault(AVA_AGENT_SECRET, cls.agent_secret)
        AgentTest.agent = Agent()
        agent_greenlet = gevent.spawn(AgentTest.agent.run)
        while not AgentTest.agent.running:
            gevent.sleep(0.5)

    @classmethod
    def tearDownClass(cls):
        AgentTest.agent.interrupted = True
        while AgentTest.agent.running:
            gevent.sleep(0.5)
