# -*- coding: utf-8 -*-

import os
import unittest
import tempfile

from ava.runtime import config


class RuntimeConfigTests(unittest.TestCase):

    def setUp(self):
        self.config = config.agent()

    def test_global_config(self):
        self.assertIsNotNone(self.config)

    def test_default_values_exist(self):
        self.assertIsNotNone(self.config.get('DEFAULT', 'pkgs_dir'))
        self.assertIsNotNone(self.config.get('DEFAULT', 'conf_dir'))
        self.assertIsNotNone(self.config.get('DEFAULT', 'data_dir'))
        self.assertIsNotNone(self.config.get('DEFAULT', 'logs_dir'))

        self.assertEqual(self.config.getint('webfront', 'listen_port'), 5000)

    def test_save_and_load_config_file(self):
        handle, filepath = tempfile.mkstemp()
        conf = config.ConfigFile(filepath)
        conf.add_section('test')
        conf.set('test', 'name', 'value')
        conf.save()

        conf2 = config.ConfigFile(filepath)
        conf2.load()
        self.assertEqual('value', conf2.get('test', 'name'))

        os.remove(filepath)
