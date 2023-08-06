# -*- coding: utf-8 -*-

"""
Configuration file reading/writing.
"""
from __future__ import absolute_import, division, print_function, unicode_literals

import logging
import logging.config
import os.path
from ConfigParser import SafeConfigParser

from ava.runtime import environ


AGENT_CONF = os.path.join(environ.conf_dir(), u'agent.ini')
LOGGING_CONF = os.path.join(environ.conf_dir(), u'logging.ini')
PACKAGES_CONF = os.path.join(environ.conf_dir(), u'packages.ini')

# The default configuration file is located at the base directory.

_defaults = dict(base_dir=environ.base_dir(),
                 conf_dir=environ.conf_dir(),
                 data_dir=environ.data_dir(),
                 pkgs_dir=environ.pkgs_dir(),
                 logs_dir=environ.logs_dir(),
                 log_file=os.path.join(environ.logs_dir(), u"ava.log"))


class ConfigFile(SafeConfigParser):
    def __init__(self, filename, defaults=_defaults):
        SafeConfigParser.__init__(self, defaults)
        self.filename = os.path.abspath(filename)

    def load(self):
        self.read(self.filename)

    def save(self):
        with open(self.filename, 'wb') as fp:
            self.write(fp)


_agent = None


def agent(file=AGENT_CONF):
    global _agent
    if not _agent:
        _agent = ConfigFile(file)
        _agent.add_section('agent')
        _agent.add_section('webfront')
        _agent.add_section('data')
        _agent.add_section('extension')
        # set defaults for various sections.

        _agent.set('webfront', 'listen_port', '5000')
        _agent.set('webfront', 'listen_addr', '127.0.0.1')

        # loads more options from file.
        _agent.load()

    return _agent

_packages = None


def packages(conf_file=PACKAGES_CONF):
    global _packages
    if not _packages:
        _packages = ConfigFile(conf_file)
        _packages.load()

    return _packages

# configure logging

logging.config.fileConfig(LOGGING_CONF, defaults=_defaults)

