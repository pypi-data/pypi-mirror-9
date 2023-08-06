# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import unittest
from io import BytesIO
from msgpack import Packer, Unpacker, packb, unpackb


class Data(dict):
    def __init__(self, name):
        super(Data, self).__init__()
        self['name'] = name

    def __getattr__(self, item):
        return self[item]


class MsgPackTest(unittest.TestCase):

    def test_packer_unpacker(self):
        buf = BytesIO()
        packer = Packer()
        buf.write(packer.pack(1))
        buf.write(packer.pack('2'))
        buf.write(packer.pack({}))
        buf.seek(0)
        unpacker = Unpacker(buf)
        v1 = unpacker.unpack()
        self.assertEqual(1, v1)

        v2 = unpacker.unpack()
        self.assertEqual('2', v2)

        v3 = unpacker.unpack()
        self.assertTrue(isinstance(v3, dict))

    def test_pack_dict(self):
        data = {'name': 'test1'}
        packed = packb(data)
        unpacked = unpackb(packed)
        self.assertTrue(isinstance(unpacked, dict))
        self.assertEqual('test1', unpacked['name'])

    def test_pack_tuple(self):
        data = ('a', 1, False)
        packed = packb(data)
        unpacked = unpackb(packed)

        self.assertTrue(isinstance(unpacked, list))
        self.assertEqual(unpacked[0], 'a')
        self.assertEqual(unpacked[1], 1)
        self.assertEqual(unpacked[2], False)

    def test_pack_object(self):
        data = Data('test')
        packed = packb(data)
        unpacked = unpackb(packed)
        self.assertEqual(unpacked['name'], 'test')