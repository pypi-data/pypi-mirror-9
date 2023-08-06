# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import webbrowser
import multiprocessing
import logging
from abc import ABCMeta, abstractmethod

from ava.runtime import settings

STR_STATUS = 'Ava - running...'
STR_OPEN_WEBFRONT = u'Open Webfront'
STR_EXIT = u'Quit Ava'

logger = logging.getLogger(__name__)


def start_server_process():
    """
    Starts the server in the forked process.
    :return: None
    """
    from ava.core.agent import start_agent
    start_agent()


class Supervisor(object):
    """
    Responsible for monitor and manage the server process.
    """
    def __init__(self, target=start_server_process):
        self.server_process = None
        self.restarted_times = 0
        self.target = target

    def start_server(self):
        if self.is_server_running():
            return

        self.server_process = multiprocessing.Process(target=self.target)
        self.server_process.start()

    def stop_server(self):
        if self.server_process is not None:
            self.server_process.terminate()
            self.server_process.join()

        self.server_process = None

    def is_server_running(self):
        return self.server_process is not None

    def health_check(self):
        """
        :return True if everything is OK.
        """

        if not self.is_server_running():
            logger.debug("Server is not running, no check.")
            return

        #logger.debug("Doing check.")
        exitcode = self.server_process.exitcode

        if exitcode is None:
            return True

        if exitcode < 0 or exitcode == 1:
            if self.restarted_times > 5:
                logger.error("Server restarted more than 5 times, give up!")
                self.server_process = None
                return False

            self.server_process = multiprocessing.Process(target=start_server_process)
            self.server_process.start()
            self.restarted_times += 1
            logger.warning("Server process restarted.")
            return True
        else:
            logger.info("Server process exited.")
            self.server_process = None
            return False


class ShellBase(object):
    """
    Base class for Shell implementations.
    Shell is responsible for launching server process and provides machinery for the user to stop it.
    """
    __metaclass__ = ABCMeta

    def __init__(self):
        port = settings['webfront']['listen_port']
        self.base_url = "http://127.0.0.1:%d/" % (port,)
        self.supervisor = Supervisor()
        self.shell_stopped = False

    def open_main_ui(self):
        webbrowser.open(self.base_url)

    def is_server_running(self):
        return self.supervisor.is_server_running()

    def set_base_url(self, url):
        self.base_url = url

    def start_server(self):
        self.supervisor.start_server()

    def stop_server(self):
        self.supervisor.stop_server()

    def check_server(self):
        """
        Checks if server process in running.
        """
        #logger.debug("Checking server status...")

        if not self.supervisor.health_check():
            self.shell_stopped = True

    def _on_idle(self):
        """
        Subclass should run this method from time to time.
        """
        self.check_server()

    def do_run(self):
        self.start_server()

        try:
            self.run()
            logger.debug("Shell is stopping.")
        finally:
            logger.debug("Stopping server")
            self.stop_server()

    @abstractmethod
    def run(self):
        """
        Subclass must implement this method to launch the shell.
        """


