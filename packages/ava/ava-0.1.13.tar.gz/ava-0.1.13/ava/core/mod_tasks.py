# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals
"""
Loading modules that provide task codes.
"""
import os
import sys
import glob
import logging
from importlib import import_module
from ava.runtime import environ
from ava.spi.signals import MODULE_LOADED

logger = logging.getLogger(__name__)

_MODULES_DIR = os.path.join('mods', 'tasks')

# the package name for modules.
_MODULE_PKG = 'mods.tasks.'


class ModuleInfo(object):

    def __init__(self, name, mod):
        self._name = name
        self._mod = mod

    @property
    def name(self):
        return self._name

    @property
    def module(self):
        return self._mod

    @module.setter
    def module(self, mod):
        self._mod = mod


class TaskModEngine(object):
    """
    Responsible for managing application modules.
    """

    def __init__(self):
        self.modules = {}
        self.modules_path = os.path.join(environ.pod_dir(), _MODULES_DIR)
        self.modules_path = os.path.abspath(self.modules_path)

    def _scan_modules(self):
        pattern = os.path.join(self.modules_path, '[a-zA-Z][a-zA-Z0-9_]*.py')
        return glob.glob(pattern)

    def _load_modules(self, ctx):
        sys.path.append(environ.pod_dir())
        logger.debug("Tasks module directory: %s", self.modules_path)

        module_files = self._scan_modules()

        logger.debug("Found %d task module(s)" % len(module_files))

        for s in module_files:
            name = os.path.basename(s)
            if '__init__.py' == name:
                continue

            # gets the basename without extension part.
            name = os.path.splitext(name)[0]
            try:
                logger.debug("Loading task module: %s", name)
                mod = import_module(_MODULE_PKG + name)
                mod_info = ModuleInfo(name, mod)
                self.modules[name] = mod_info

                ctx.send(signal=MODULE_LOADED, sender=self)
            except ImportError:
                logger.error("Failed to import task module: %s", name, exc_info=True)

    def start(self, ctx):
        logger.debug("Starting task module engine...")
        self._load_modules(ctx)
        logger.debug("Task module engine started.")

    def stop(self, ctx):
        logger.debug("Task module engine stopped.")