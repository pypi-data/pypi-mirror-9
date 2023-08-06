# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import time

from ava.shell.base import ShellBase


class Shell(ShellBase):
    """
    Shell used in text console.
    """
    def __init__(self):
        super(Shell, self).__init__()

    def run(self):
        while not self.shell_stopped:
            try:
                time.sleep(1)
                super(Shell, self).check_server()
            except KeyboardInterrupt:
                break
