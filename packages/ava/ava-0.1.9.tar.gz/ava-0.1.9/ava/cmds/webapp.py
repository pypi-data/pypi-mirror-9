# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import click
from .cli import cli
from ava.runtime import settings


@cli.command()
@click.argument("app")
def launch(app):
    """ Launch web application.
    """
    click.launch('http://127.0.0.1:%s' % settings['webfront']['listen_port'])