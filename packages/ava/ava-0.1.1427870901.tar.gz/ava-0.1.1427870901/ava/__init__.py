# -*- coding: utf-8 -*-
import time

VERSION_MAJOR = 0
VERSION_MINOR = 1
VERSION_MICRO = time.time()

__version__ = '%d.%d.%d' % (VERSION_MAJOR, VERSION_MINOR, VERSION_MICRO)
VERSION_STRING = __version__

