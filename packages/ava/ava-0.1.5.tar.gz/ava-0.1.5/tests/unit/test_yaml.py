# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function)

import os
import unittest
from yaml import load, dump
from ava.util import base_path

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class YamlConfigTest(unittest.TestCase):
    def setUp(self):
        self.conf_file = os.path.join(base_path(), 'tests', 'data', 'test.yml')

    def test_can_load_yaml_file(self):
        fin = file(self.conf_file)
        data = load(fin, Loader=Loader)
        # print(data)
        self.assertTrue(isinstance(data, dict))

    def test_can_dump_yaml_file(self):
        data = {
            'a': "a",
            'b': "b",
            'sample': {
                'k1': 'v1'
            }
        }
        self.assertTrue(isinstance(data, dict))
        output = dump(data, Dumper=Dumper)

        self.assertTrue("sample" in output)