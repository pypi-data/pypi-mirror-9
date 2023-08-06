# -*- coding: utf-8 -*-

from __future__ import print_function

import os
import unittest
import lmdb
import tempfile
import shutil


class TestLMDB(unittest.TestCase):

    def setUp(self):
        self.path = tempfile.mkdtemp()
        self.lmdb = lmdb.Environment(self.path, max_dbs=4)

    def tearDown(self):
        self.lmdb.close()
        shutil.rmtree(self.path)

    def test_info(self):
        print(self.lmdb.info())
        print("Max key size: ", self.lmdb.max_key_size())

    def test_crud(self):
        with self.lmdb.begin(write=True) as txn:
            txn.put("k1", "value1")

            v1 = txn.get("k1")
            self.assertEqual(v1, "value1")

            txn.put("k1", "value2")
            v2 = txn.get("k1")
            self.assertEqual(v2, "value2")

            txn.delete("k1")

            v3 = txn.get("k1")
            self.assertTrue(v3 is None)

    def test_subdb(self):
        db = self.lmdb.open_db("test", create=True)

        self.assertIsNotNone(db, "db should not be none.")

        with self.lmdb.begin(write=False) as txn:
            cur = txn.cursor()
            for k, v in iter(cur):
                print("Found db: ", k)


