# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import click
import pip
from .cli import cli
from ava.runtime import environ


@cli.group()
def pkg():
    """ package management.
    """
    pass


@pkg.command()
@click.argument("query", type=click.STRING)
def search(query):
    pip.main(['search', query])

@pkg.command()
@click.argument("requirement")
def install(requirement):
    pip.main(['install', '--target=%s' % environ.pkgs_dir(), requirement])