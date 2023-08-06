# -*- coding: utf-8 -*-
from __future__ import print_function, division, absolute_import

import unittest
import re

from ava.util import resource_path, time_uuid
from ava.util import webutils


class UtilTest(unittest.TestCase):

    def test_resource_path(self):
        rv = resource_path("path1")
        print(rv)
        self.assertTrue(rv.endswith("path1"))

    def test_time_uuid(self):
        prev = time_uuid.utcnow()
        for i in xrange(1000):
            now = time_uuid.utcnow()
            #print(now.hex)
            self.assertTrue(now > prev)
            prev = now


    def test_parse_authorization_header(self):
        result = webutils.parse_authorization_header('EAvatar key="1234",realm="http://eavatar.me", token="abcd"')
        self.assertEqual("eavatar", result['scheme'])
        self.assertEqual("http://eavatar.me", result["realm"])
        self.assertEqual("1234", result["key"])
        self.assertEqual("abcd", result["token"])

    def test_store_url_without_path(self):
        store_without_path = '/a/QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY/store'
        store_with_path = '/a/QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY/store/this/is/a/path?q=test'
        pattern = '^\/a/([a-zA-Z0-9]+)/store(/[^\?]*)?'
        pat = re.compile(pattern)
        matches = pat.match(store_without_path)
        self.assertEqual('/a/QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY/store', matches.group(0))
        self.assertEqual('QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY', matches.group(1))
        self.assertIsNone(matches.group(2))

    def test_store_url_with_path(self):
        store_with_path = '/a/QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY/store/this/is/a/path?q=test'
        pattern = '^\/a/(?P<aid>[a-zA-Z0-9]+)/store(?P<path>/[^\?]*)?'
        pat = re.compile(pattern)
        matches = pat.match(store_with_path)
        self.assertEqual('/a/QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY/store/this/is/a/path', matches.group(0))
        self.assertEqual('QPndzFJTmycdfg5jxcSghX2scJnc3TNqVEfYtVTA5JVYiPQY', matches.group('aid'))
        self.assertEqual('/this/is/a/path', matches.group('path'))