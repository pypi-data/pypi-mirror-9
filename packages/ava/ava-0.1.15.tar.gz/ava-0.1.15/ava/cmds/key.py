# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division,
                        print_function, unicode_literals)
import os
import json
import click
from ava.util import crypto
from ava.util import yaml
from ava.runtime import environ
from .cli import cli


def gen_random_key(ctx):
    if ctx.obj['verbosity']:
        click.echo("Generating random key...")
    (pk, sk) = crypto.generate_keypair()
    xid = crypto.key_to_xid(pk)
    secret_str = crypto.secret_to_string(sk)
    key_str = crypto.key_to_string(pk)
    res = dict(xid=xid, key=key_str, secret=secret_str)
    click.echo(json.dumps(res, sort_keys=True, indent=4, separators=(',', ': ')))
    return 0


@cli.group()
@click.pass_context
def key(ctx):
    """ Key management
    """
    pass


@key.command()
@click.option('--email', prompt='Your email address', help='Email address')
@click.option('--password',
              prompt='Your password',
              hide_input=True,
              confirmation_prompt=True,
              help='Your password')
@click.option('--force', '-f',
              help='Force to generate new keys even if already exists.')
@click.pass_context
def user(ctx, email, password, force=False):
    """ Set up user keys.
    """
    filepath = os.path.join(ctx.obj['app_dir'], 'user-keys.yml')
    if os.path.exists(filepath) and not force:
        click.echo('Keys already exist, use --force option to replace.',
                   err=True)
        click.confirm('Do you want to overwrite it?', abort=True)

    content = {}
    secret = crypto.derive_secret_key(password=password.encode('utf-8'),
                                      salt=email.encode('utf-8'))
    content[b'xid'] = crypto.secret_key_to_xid(secret)
    content[b'email'] = email

    oldmask = os.umask(077)
    with open(filepath, 'wb') as keyfile:
        yaml.dump(content, keyfile)
    os.umask(oldmask)
    if ctx.obj['verbosity'] > 0:
        click.echo('Key file generated.')


@key.command()
@click.option('--force', '-f',
              help='Force to generate new keys even if already exists.')
@click.pass_context
def agent(ctx, force=False):
    """ Generate keys for agent.
    """
    userkeys_path = os.path.join(ctx.obj['app_dir'], 'user-keys.yml')
    if not os.path.exists(userkeys_path):
        click.echo('You should set user keys first.', err=True)
        return

    with open(userkeys_path, 'rb') as userkeys_file:
        userkeys = yaml.load(userkeys_file)
    user_xid = userkeys.get('xid')

    agentkeys_path = os.path.join(environ.conf_dir(), 'ava-keys.yml')
    if os.path.exists(agentkeys_path) and not force:
        click.echo('Agent keys exist!')
        click.confirm('Do you want to overwrite it?', abort=True)

    content = {}
    pk, sk = crypto.generate_keypair()

    content[b'user'] = user_xid
    content[b'secret'] = crypto.secret_to_string(sk)

    with open(agentkeys_path, 'wb') as agentkeys_file:
        yaml.dump(content, agentkeys_file)


@key.command()
@click.option('--salt', '-s',
              help='Value for increasing randomness, e.g. email address.')
@click.option('--password', '-p',
              help='Hard to guess password.')
@click.pass_context
def generate(ctx, salt=None, password=None):
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

    sk = crypto.derive_secret_key(password, salt)
    (pk, sk) = crypto.generate_keypair(sk=sk)
    xid = crypto.key_to_xid(pk)
    secret_str = crypto.secret_to_string(sk)
    key_str = crypto.key_to_string(pk)
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
        if crypto.validate_xid(xid):
            click.echo("XID %s is valid." % xid)
        else:
            click.echo("XID %s is invalid." % xid)

    if key:
        if crypto.validate_key_string(key):
            click.echo("Key is valid")
        else:
            click.echo("Key is invalid.")

    if secret:
        if crypto.validate_secret_string(secret):
            click.echo("Secret is valid.")
        else:
            click.echo("Secret is invalid.")

    if key and secret:
        sk = crypto.string_to_secret(secret)
        pk = crypto.string_to_key(key)
        (vpk, vsk) = crypto.generate_keypair(sk=sk)
        if vpk == pk and vsk == sk:
            click.echo("Key and secret are matched.")
            return 0
        click.echo("Key and secret are mismatched.")
        return 1

