# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import hashlib
import pyscrypt
import base58
import libnacl.public
import libnacl.secret

XID_PREFIX = b'\x5f'
KEY_PREFIX = b'\xba'  # prefix for public key string
SECRET_PREFIX = b'\xff'  # prefix for secret key string


def generate_keypair(sk=None):
    """
    Generate a random key pair.
    :return:
    """
    if sk:
        keypair = libnacl.public.SecretKey(sk=sk)
    else:
        keypair = libnacl.public.SecretKey()

    return keypair.pk, keypair.sk


def key_to_xid(key):
    """
    Generate an address from a public key.
    :param key: the 32-byte byte string.
    :return:
    """
    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(key)
    sum = sha256.digest()
    addr = XID_PREFIX + key + sum[:2]

    return base58.b58encode(addr)


def validate_xid(addr):
    """
    Check if the provided address is valid or not.

    :param addr: address in base58 string.
    :return:
    """
    val = base58.b58decode(addr)
    #assert len(val) == 35

    if len(val) != 35:
        return False

    prefix = val[0]
    if prefix != XID_PREFIX:
        return False

    sha256 = hashlib.sha256()
    sha256.update(XID_PREFIX)
    sha256.update(val[1:33])
    sum = sha256.digest()

    if val[-2:] != sum[:2]:
        return False

    return True


def derive_secret_key(password, salt):
    if isinstance(password, unicode):
        password = password.encode('utf-8')
    if isinstance(salt, unicode):
        salt = salt.encode('utf-8')

    sk = pyscrypt.hash(password=password,
                       salt=salt,
                       N=1024,
                       r=1,
                       p=1,
                       dkLen=32)
    return sk


def secret_to_string(key):
    """
    Converts a secret key to its string form
    :param key: the secret key
    :return: a string equivalent to the secret key
    """
    sha256 = hashlib.sha256()
    sha256.update(SECRET_PREFIX)
    sha256.update(key)
    sum = sha256.digest()
    result = SECRET_PREFIX + key + sum[:2]

    return base58.b58encode(result)


def string_to_secret(sk_str):
    val = base58.b58decode(sk_str)

    if len(val) != 35:
        return None

    prefix = val[0]
    if prefix != SECRET_PREFIX:
        return None

    key = val[1:33]
    sha256 = hashlib.sha256()
    sha256.update(SECRET_PREFIX)
    sha256.update(key)
    s = sha256.digest()

    if val[-2:] != s[:2]:
        return None

    return key


def validate_secret_string(sk_str):
    """
    Validates a given public key string.
    :param sk_str:
    :return:
    """
    val = base58.b58decode(sk_str)

    if len(val) != 35:
        return False

    prefix = val[0]
    if prefix != SECRET_PREFIX:
        return False

    sha256 = hashlib.sha256()
    sha256.update(SECRET_PREFIX)
    sha256.update(val[1:33])
    s = sha256.digest()

    if val[-2:] != s[:2]:
        return False

    return True


def key_to_string(key):
    """
    Converts a public key to its string form
    :param key: the public key
    :return:
    """
    sha256 = hashlib.sha256()
    sha256.update(KEY_PREFIX)
    sha256.update(key)
    sum = sha256.digest()
    result = KEY_PREFIX + key + sum[:2]

    return base58.b58encode(result)


def string_to_key(pk_str):
    val = base58.b58decode(pk_str)

    if len(val) != 35:
        return None

    prefix = val[0]
    if prefix != KEY_PREFIX:
        return None

    key = val[1:33]
    sha256 = hashlib.sha256()
    sha256.update(KEY_PREFIX)
    sha256.update(key)
    s = sha256.digest()

    if val[-2:] != s[:2]:
        return None

    return key


def validate_key_string(pk_str):
    """
    Validates a given public key string.
    :param sk_str:
    :return:
    """
    val = base58.b58decode(pk_str)
    #assert len(val) == 35

    if len(val) != 35:
        return False

    prefix = val[0]
    if prefix != KEY_PREFIX:
        return False

    sha256 = hashlib.sha256()
    sha256.update(KEY_PREFIX)
    sha256.update(val[1:33])
    s = sha256.digest()

    if val[-2:] != s[:2]:
        return False

    return True

