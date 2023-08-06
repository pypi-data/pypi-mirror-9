# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import logging
import gevent
import unittest
from ava.core.task import TaskEngine
from ava.spi.context import Context
from ava.spi.task import task

counter = 0



class TaskEngineTests(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(level=logging.DEBUG)
        self.engine = TaskEngine()
        self.ctx = Context(None)
        self.ctx.bind('taskengine', self.engine)
        self.engine.start(self.ctx)
        self.logger = logging.getLogger(__name__)

    def tearDown(self):
        self.engine.stop(self.ctx)

    def test_register_and_unregister_task(self):

        def mock_task1():
            return True

        t1 = self.engine.register(mock_task1)
        task_key = __name__ + '.mock_task1'
        self.assertEqual(t1.key, task_key)

        self.engine.unregister(task_key)

        self.assertIsNone(self.engine.get_task(task_key))

    def test_once_schedule(self):
        def mock_task2():
            self.logger.debug("mock_task2() run.")
            return True

        t1 = self.engine.register(mock_task2)
        task_key = __name__ + '.mock_task2'
        schedule1 = t1.run_once()
        schedule1.join()
        self.assertTrue(schedule1.result)

    def test_periodic_schedule(self):
        global counter
        counter = 0

        def mock_task3():
            global counter
            counter += 1
            return counter

        t1 = self.engine.register(mock_task3)

        sched = t1.run_periodic(0.1)
        gevent.sleep(1)
        self.assertTrue(sched.result > 5)

    def test_cancel_schedule(self):
        def mock_once_task():
            return True

        t1 = self.engine.register(mock_once_task)
        schedule1 = t1.run_once(delayed_secs=10)
        got_sched = self.engine.get_schedule(schedule1.id)
        self.assertIsNotNone(got_sched)

        self.engine.cancel(schedule1)
        got_sched = self.engine.get_schedule(schedule1.id)
        self.assertIsNone(got_sched)
