# -*- coding: utf-8 -*-

from __future__ import print_function

import unittest
import mock

from ava.spi.context import Context
from ava.core.data import DataEngine


class TestDataEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DataEngine()
        self.ctx = Context(None)
        self.ctx.bind('dataengine', self.engine)
        self.engine.start(self.ctx)

    def tearDown(self):
        self.engine.remove_all_stores()
        self.engine.stop(self.ctx)

    def test_create_and_remove_store(self):
        store = self.engine.get_store("testdb")
        self.assertIsNone(store)

        store = self.engine.create_store("testdb")
        self.assertIsNotNone(store)

        store = self.engine.get_store("testdb")
        self.assertIsNotNone(store)
        store2 = self.engine.get_store("testdb")
        self.assertIs(store, store2)

        self.assertTrue("testdb" in self.engine)
        store = self.engine['testdb']
        self.assertIs(store, store2)

        del self.engine["testdb"]
        store = self.engine.get_store("testdb")
        self.assertFalse(self.engine.store_exists("testdb"))

    def test_crud(self):
        store = self.engine.create_store("testdb2")
        self.assertIsNotNone(store)

        with self.engine.cursor("testdb2", readonly=False) as cur:
            ret1 = cur.put('doc1', 'value1')
            self.assertTrue(ret1)
            cur.put('doc2', 'value2')
            cur.put('doc3', b"中文")

        with self.engine.cursor("testdb2") as cur:
            val1 = cur.load("doc1")
            self.assertEqual("value1", val1)
            val3 = cur.load("doc3")
            self.assertEqual(b"中文", val3)

        with self.engine.cursor("testdb2", readonly=False) as cur:
            cur.remove("doc2")
            doc2 = cur.get("doc2")
            self.assertIsNone(doc2)

        self.engine.remove_store("testdb2")

    def test_crud_with_store(self):
        store = self.engine.create_store("testdb2")
        self.assertIsNotNone(store)

        store['doc1'] = 'value1'
        store['doc2'] = 'value2'
        store['doc3'] = b"中文"

        self.assertEqual(len(store), 3)
        self.assertTrue('doc1' in store)

        self.assertEqual("value1", self.engine['testdb2']['doc1'])
        self.assertEqual(b"中文", store['doc3'])

        del store['doc2']
        self.assertIsNone(store['doc2'])

        # it's ok to delete nonexistent entry
        del store['doc2']

        self.engine.remove_store("testdb2")

    def test_seek_and_seek_range(self):
        store = self.engine.create_store("testdb2")
        self.assertIsNotNone(store)

        store[b'doc1'] = b'value1'
        store[b'doc2'] = b'value2'
        store[b'doc3'] = b'value3'

        with self.engine.cursor("testdb2", readonly=True) as cur:
            self.assertTrue(cur.seek('doc2'))
            self.assertTrue(b'doc2', cur.key())
            self.assertTrue(b'value2, cur.value')

            self.assertTrue(cur.seek_range('doc'))
            self.assertEqual(b'doc1', cur.key())
            self.assertFalse(cur.seek_range('doc4'))

        self.engine.remove_store("testdb2")

    def test_transaction_abort(self):
        store = self.engine.create_store("testdb2")
        self.assertIsNotNone(store)

        try:
            with self.engine.cursor("testdb2", readonly=False) as cur:
                cur.put('_id', "k1")
                cur.put('_id', "k2")
                raise Exception()
        except:
            pass

        with self.engine.cursor("testdb2") as cur:
            self.assertIsNone(cur.get("k1"))
            self.assertIsNone(cur.get("k2"))

        self.engine.remove_store("testdb2")

    def test_forward_iterator(self):
        store = self.engine.create_store("testdb2")
        self.assertIsNotNone(store)

        with self.engine.cursor("testdb2", readonly=False) as cur:
            cur.put('k1', 'value3')
            cur.put('k2', 'value1')
            cur.put('k3', 'value2')

        with self.engine.cursor("testdb2") as cur:
            cur.seek("k1")

            it = cur.iternext()
            self.assertEqual("k1", it.next())
            self.assertEqual("k2", it.next())
            self.assertEqual("k3", it.next())

        self.engine.remove_store("testdb2")

    def test_backward_iterator(self):
        store = self.engine.create_store("testdb2")
        self.assertIsNotNone(store)

        with self.engine.cursor("testdb2", readonly=False) as cur:
            cur.put('k1', 'value3')
            cur.put('k2', 'value1')
            cur.put('k3', 'value2')

        with self.engine.cursor("testdb2") as cur:
            cur.last()

            it = cur.iterprev()
            self.assertEqual("k3", it.next())
            self.assertEqual("k2", it.next())
            self.assertEqual("k1", it.next())

        self.engine.remove_store("testdb2")

    def test_post_and_pop(self):
        store = self.engine.create_store("queue")
        with self.engine.cursor("queue", readonly=False) as cur:
            cur.post('v1')
            cur.post('v2')
            cur.post('v3')

        with self.engine.cursor("queue", readonly=False) as cur:
            self.assertEqual('v1', cur.pop())
            self.assertEqual('v2', cur.pop())
            self.assertEqual('v3', cur.pop())
            self.assertIsNone(cur.pop())

        self.engine.remove_store("queue")

