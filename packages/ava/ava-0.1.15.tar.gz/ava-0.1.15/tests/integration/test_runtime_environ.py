# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import os
import unittest

from ava.runtime import environ


class RuntimeEnvironTest(unittest.TestCase):

    def test_work_home(self):
        env = environ.Environment()
        self.assertTrue(os.path.isdir(env.pod_dir))
        self.assertTrue(os.path.isdir(env.conf_dir))
        self.assertTrue(os.path.isdir(env.data_dir))
        self.assertTrue(os.path.isdir(env.logs_dir))
        self.assertTrue(os.path.isdir(env.pkgs_dir))

