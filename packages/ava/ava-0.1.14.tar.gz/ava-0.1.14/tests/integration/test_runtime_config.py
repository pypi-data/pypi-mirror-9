# -*- coding: utf-8 -*-

import unittest

from ava.runtime import settings


class RuntimeConfigTests(unittest.TestCase):

    def test_should_have_dir_settings(self):
        self.assertIsNotNone(settings.get('pkgs_dir'))
        self.assertIsNotNone(settings.get('conf_dir'))
        self.assertIsNotNone(settings.get('data_dir'))
        self.assertIsNotNone(settings.get('logs_dir'))

    def test_should_have_settings_for_webfront(self):
        self.assertIsNotNone(settings['webfront']['listen_port'])

    def test_should_have_logging_settings(self):
        handlers = settings['logging']['handlers']
        self.assertIsNotNone(handlers)
        log_file = handlers['file_handler']['filename']
        #print(log_file)
        self.assertIsNotNone(log_file)


