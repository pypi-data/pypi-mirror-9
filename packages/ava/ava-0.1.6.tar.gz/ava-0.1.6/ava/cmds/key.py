# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)

import json
import click
from ava.util import key as keyutil
from .cli import cli


def gen_random_key(ctx):
    if ctx.obj['verbose']:
        click.echo("Generating random key...")
    (pk, sk) = keyutil.generate_keypair()
    xid = keyutil.key_to_xid(pk)
    secret_str = keyutil.secret_to_string(sk)
    key_str = keyutil.key_to_string(pk)
    res = dict(xid=xid, key=key_str, secret=secret_str)
    click.echo(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
    return 0


@cli.group()
@click.pass_context
def key(ctx, verbose):
    """ Key management
    """
    ctx.obj = dict(verbose=verbose)


@key.command()
@click.option('--salt', '-s',
              help='Value for increasing randomness, e.g. email address.')
@click.option('--password', '-p',
              help='Hard to guess password.')
@click.pass_context
def generate(ctx, salt, password):
    """ Generate random key or derive from salt and password.

    """
    if not salt and not password:
        return gen_random_key(ctx)

    if not (salt and password):
        if not salt:
            click.echo("Missing option: salt")
        if not password:
            click.echo("Missing option: password")
        return 1

    sk = keyutil.derive_secret_key(password, salt)
    (pk, sk) = keyutil.generate_keypair(sk=sk)
    xid = keyutil.key_to_xid(pk)
    secret_str = keyutil.secret_to_string(sk)
    key_str = keyutil.key_to_string(pk)
    res = dict(xid=xid, key=key_str, secret=secret_str)
    click.echo(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
    return 0


@key.command()
@click.option('--xid', '-i',
              help='Exchange ID')
@click.option('--key', '-k',
              help='Public key')
@click.option('--secret', '-s',
              help='Secret key')
@click.pass_context
def validate(ctx, xid, key, secret):
    """
    Validate XID, public key or secret key.

    :param ctx:
    :param xid:
    :param key:
    :param secret:
    :return:
    """
    if xid:
        if keyutil.validate_xid(xid):
            click.echo("XID %s is valid." % xid)
        else:
            click.echo("XID %s is invalid." % xid)

    if key:
        if keyutil.validate_key_string(key):
            click.echo("Key is valid")
        else:
            click.echo("Key is invalid.")

    if secret:
        if keyutil.validate_secret_string(secret):
            click.echo("Secret is valid.")
        else:
            click.echo("Secret is invalid.")

    if key and secret:
        sk = keyutil.string_to_secret(secret)
        pk = keyutil.string_to_key(key)
        (vpk, vsk) = keyutil.generate_keypair(sk=sk)
        if vpk == pk and vsk == sk:
            click.echo("Key and secret are matched.")
            return 0
        click.echo("Key and secret are mismatched.")
        return 1

