# -*- coding: utf-8 -*-

"""
Configuration file reading/writing.
"""
from __future__ import absolute_import, division, print_function, \
    unicode_literals

import codecs
import logging
import logging.config
import os.path
from bottle import template

from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

from ava.runtime import environ


AGENT_CONF = os.path.join(environ.conf_dir(), u'ava.yml')

# The default configuration file is located at the base directory.

settings = dict(base_dir=environ.base_dir(),
                conf_dir=environ.conf_dir(),
                data_dir=environ.data_dir(),
                pkgs_dir=environ.pkgs_dir(),
                logs_dir=environ.logs_dir(),
                mods_dir=environ.mods_dir(),
                )


def load_conf(conf_file):
    if not os.path.exists(conf_file):
        return {}

    data = codecs.open(conf_file, 'rb', encoding='utf-8').read()
    if len(data.strip()) == 0:
        return {}

    data = template(data, **settings)
    return load(data, Loader=Loader)


def save_conf(conf_file, content):
    out = codecs.open(conf_file, 'wb', encoding='utf-8')
    out.write(dump(content, Dumper=Dumper, default_flow_style=False,
                   indent=4, width=80))

settings.update(load_conf(AGENT_CONF))

# configure logging
logging.config.dictConfig(settings['logging'])
