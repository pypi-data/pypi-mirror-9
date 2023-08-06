# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

from gevent import monkey
monkey.patch_all()

import time
import unittest
import mock
import threading
from ava.shell.console import Shell


class ShellTest(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch('ava.shell.base.Supervisor')
    def test_console(self, mock_supervisor):
        mc = mock_supervisor
        ms = mock_supervisor.return_value
        ms.is_server_running.return_value = False
        ms.healthcheck.return_value = True
        shell = Shell()

        self.assertTrue(mc.called)
        shell.is_server_running()
        self.assertTrue(ms.is_server_running.called)
        self.assertFalse(shell.is_server_running())

        t = threading.Thread(target=shell.do_run)
        t.start()
        time.sleep(0.1)
        self.assertTrue(ms.start_server.called)

        ms.is_server_running.return_value = True
        self.assertTrue(shell.is_server_running())
        shell.shell_stopped = True
        t.join()


    @mock.patch('ava.shell.base.Supervisor')
    def test_console_with_bad_health_check(self, mock_supervisor):
        mc = mock_supervisor
        ms = mock_supervisor.return_value
        ms.is_server_running.return_value = False
        ms.health_check.return_value = True
        shell = Shell()

        self.assertTrue(mc.called)
        shell.is_server_running()
        self.assertTrue(ms.is_server_running.called)
        self.assertFalse(shell.is_server_running())

        t = threading.Thread(target=shell.do_run)
        t.start()
        time.sleep(0.1)
        self.assertTrue(ms.start_server.called)

        ms.is_server_running.return_value = True
        self.assertTrue(shell.is_server_running())

        ms.health_check.return_value = False
        t.join()
        self.assertTrue(shell.shell_stopped)

