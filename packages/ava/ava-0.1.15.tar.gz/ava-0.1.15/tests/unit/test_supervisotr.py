# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import time
import unittest

import mock
from ava.shell.base import Supervisor


def server_process1():
    time.sleep(2)


class SupervisorTest(unittest.TestCase):

    @mock.patch('ava.shell.base.multiprocessing.Process')
    def test_supervisor(self, mock_process_class):
        mp = mock_process_class.return_value
        mp.exitcode = None

        supervisor = Supervisor(target=server_process1)
        self.assertFalse(supervisor.is_server_running())

        supervisor.start_server()
        self.assertTrue(mock_process_class.called)
        self.assertTrue(mp.start.called)
        self.assertTrue(supervisor.is_server_running())

        supervisor.stop_server()
        self.assertTrue(mp.terminate.called)
        self.assertFalse(supervisor.is_server_running())

    @mock.patch('ava.shell.base.multiprocessing.Process')
    def test_supervisor_with_server_abnormally_exit(self, mock_process_class):
        mp = mock_process_class.return_value
        mp.exitcode = None

        supervisor = Supervisor(target=server_process1)
        self.assertFalse(supervisor.is_server_running())

        supervisor.start_server()
        self.assertTrue(mock_process_class.called)
        self.assertTrue(mp.start.called)
        self.assertTrue(supervisor.is_server_running())

        # emulate server process exits abnormally.
        mp.exitcode = -1
        self.assertTrue(supervisor.health_check())
        self.assertEqual(mp.start.call_count, 2)

        # exitcode = 1 indicates that server requested to restart.
        mp.exitcode = 1
        self.assertTrue(supervisor.health_check())
        self.assertEqual(mp.start.call_count, 3)

        # in case that restarting too many times, supervisor should give up.
        for i in range(5):
            mp.exitcode = -1
            supervisor.health_check()

        self.assertFalse(supervisor.health_check())

        supervisor.stop_server()
        self.assertFalse(mp.terminate.called)
        self.assertFalse(supervisor.is_server_running())

    @mock.patch('ava.shell.base.multiprocessing.Process')
    def test_supervisor_with_server_normally_exit(self, mock_process_class):
        mp = mock_process_class.return_value
        mp.exitcode = None

        supervisor = Supervisor(target=server_process1)
        self.assertFalse(supervisor.is_server_running())

        supervisor.start_server()
        self.assertTrue(mock_process_class.called)
        self.assertTrue(mp.start.called)
        self.assertTrue(supervisor.is_server_running())

        # emulate server process exits normally.
        mp.exitcode = 0
        self.assertFalse(supervisor.health_check())
        self.assertEqual(mp.start.call_count, 1)

        supervisor.stop_server()
        self.assertFalse(mp.terminate.called)
        self.assertFalse(supervisor.is_server_running())
