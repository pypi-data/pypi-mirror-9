# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys
import logging

POD_DIR_ENV = 'AVA_POD'

POD_DIR_NAME = u'pod'
PKGS_DIR_NAME = u'pkgs'
LOGS_DIR_NAME = u'logs'
DATA_DIR_NAME = u'data'
CONF_DIR_NAME = u'conf'
MODS_DIR_NAME = u'mods'


class Environment(object):
    """
    Encapsulates the runtime environment.
    """
    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # Determines the location of the base directory which contains files
        # for a specific user.
        # This script assumes it is located at 'ava/runtime' sub-directory.
        from ava.util import base_path

        self.base_dir = base_path()

        # Determines the location of the home directory.

        self.pod_dir = os.path.join(self.base_dir, POD_DIR_NAME)
        self.pod_dir = os.environ.get(POD_DIR_ENV, self.pod_dir)
        self.pod_dir = os.path.abspath(self.pod_dir)
        if not os.path.isdir(self.pod_dir):
            self.logger.error("Invalid pod folder: %s" % self.pod_dir)
            sys.exit(-1)

        self.conf_dir = os.path.join(self.pod_dir, CONF_DIR_NAME)
        self.pkgs_dir = os.path.join(self.pod_dir, PKGS_DIR_NAME)
        self.data_dir = os.path.join(self.pod_dir, DATA_DIR_NAME)
        self.logs_dir = os.path.join(self.pod_dir, LOGS_DIR_NAME)
        self.mods_dir = os.path.join(self.pod_dir, MODS_DIR_NAME)

        # Flag indicating if the runtime is launched by a shell.
        self.has_shell = False


# The global environment.
_environ = None


def get_environ():
    global _environ

    if _environ is None:
        _environ = Environment()

    return _environ


def base_dir():
    """
    Gets the base directory.
    :return:
    """
    return get_environ().base_dir


def pod_dir():
    """
    Gets the home directory.
    :return:
    """
    return get_environ().pod_dir


def conf_dir():
    """
    Gets the path for configuration files.

    :return: The configuration path.
    """
    return get_environ().conf_dir


def data_dir():
    """
    Gets the path for data files.

    :return: The path.
    """
    return get_environ().data_dir


def logs_dir():
    """
    Gets the path for log files.

    :return: The path.
    """
    return get_environ().logs_dir


def pkgs_dir():
    """
    Gets the path for packages files.

    :return: The path.
    """
    return get_environ().pkgs_dir


def mods_dir():
    return get_environ().mods_dir
