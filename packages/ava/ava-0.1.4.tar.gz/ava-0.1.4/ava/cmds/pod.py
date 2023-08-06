# -*- coding: utf-8 -*-
"""
Command for managing local pod directory.
"""
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import os
import shutil
import click

from ava.runtime import environ

from .cli import cli


@cli.group()
def pod():
    """ Pod management.
    """
    pass


@pod.command()
@click.argument("folder", type=click.Path(exists=False))
def init(folder):
    """
    Constructs the skeleton of directories if it not there already.
    :return:
    """

    if os.path.exists(folder):
        click.echo("Folder %s is not empty!" % folder, err=True)
        return

    os.makedirs(folder)

    src_dir = environ.pod_dir()
    # copy files from base_dir to user_dir
    subdirs = os.listdir(src_dir)
    for d in subdirs:
        src_path = os.path.join(src_dir, d)
        dst_path = os.path.join(folder, d)
        if os.path.isdir(src_path):
            shutil.copytree(src_path, dst_path)
        else:
            shutil.copy2(src_path, dst_path)


@pod.command()
def open():
    """ Open Pod folder in a file explorer or the like.
    """
    click.launch(environ.pod_dir())