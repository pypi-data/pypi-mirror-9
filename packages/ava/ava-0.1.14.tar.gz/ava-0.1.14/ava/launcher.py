#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
The launcher for EAvatar to run in a text console or headless environment.
"""

import sys
import logging
import multiprocessing

#makes multiprocessing work when in freeze mode.
multiprocessing.freeze_support()



# prevent no handler warning
try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


logger = logging.getLogger("ava")


def main():
    from ava.cmds.cli import cli, load_commands

    load_commands()
    return cli(auto_envvar_prefix=b'AVA')

if __name__ == '__main__':
    sys.exit(main())