# -*- coding: utf-8 -*-
"""
Data engine implementation based on lighting memory database (http://symas.com/mdb/).
The Lmdb is initialized, the access needs to use its binding API, though.
Extension packages may provide higher-level APIs based on this.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import time
import logging

import lmdb
from ava.runtime import environ


_DATA_FILE_DIR = 'data'

logger = logging.getLogger(__name__)


class DataEngine(object):
    def __init__(self):
        logger.debug("Initializing data engine...")
        self.datapath = None
        self.database = None

    def start(self, ctx=None):
        logger.debug("Starting data engine...")

        self.datapath = os.path.join(environ.pod_dir(), _DATA_FILE_DIR)
        logger.debug("Data path: %s", self.datapath)

        try:
            self.database = lmdb.Environment(self.datapath, max_dbs=32)
        except lmdb.Error:
            logger.exception("Failed to open database.", exc_info=True)
            raise

        logger.debug("Data engine started.")

    def stop(self, ctx=None):
        logger.debug("Stopping data engine...")
        if self.database:
            self.database.close()

        logger.debug("Data engine stopped.")

