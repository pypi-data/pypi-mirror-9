# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import logging
import click


CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group(invoke_without_command=True, context_settings=CONTEXT_SETTINGS)
@click.option('-v', '--verbose', count=True)
@click.pass_context
def cli(ctx, verbose):
    """ The command-line interface for Ava.
    """
    ctx.obj = dict(verbosity=verbose)

    log_level = logging.WARNING

    if verbose > 1:
        log_level = logging.DEBUG
    elif verbose == 1:
        log_level = logging.INFO

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=log_level, disable_existing_loggers=False)

    app_dir = click.get_app_dir('.ava')
    if not os.path.exists(app_dir):
        os.makedirs(app_dir, 0700)
    if verbose > 2:
        click.echo("Location for configuration files: %s" % app_dir)

    ctx.obj['app_dir'] = app_dir

    if ctx.invoked_subcommand is None:
        from .agent import run
        ctx.invoke(run)