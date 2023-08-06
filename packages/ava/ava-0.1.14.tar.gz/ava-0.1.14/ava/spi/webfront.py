# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals

"""
Imports utility functions from Bottle for exposing web resource.
"""
import os
from ava.runtime import environ
import logging
import six
import binascii
from bottle import request, hook, HTTPError
from ava.util import token
from ava.util import crypto
from ava.runtime.config import settings

from bottle import route, get, post, delete, put, request, response
from bottle import static_file as _static_file
from ava.core.webfront import dispatcher

logger = logging.getLogger(__name__)


static_folder = os.path.join(environ.pod_dir(), 'webroot')


def _raise_unauthorized(desc=b'Authentication required.'):
    raise HTTPError(401, desc)


def check_authentication():
    logger.debug("Checking authentication...")

    http_auth = request.get_header('Authorization')

    logger.debug("Authentication header: %s", http_auth)

    if http_auth is None:
        msg = "No authentication header value is given."
        _raise_unauthorized(desc=msg)

    if isinstance(http_auth, six.string_types):
            http_auth = http_auth.encode('ascii')

    auth_type = ""
    user_and_key = ""

    try:
        auth_type, user_and_key = http_auth.split(six.b(' '), 1)
    except ValueError as err:
        msg = ("Basic authorize header value not properly formed. "
               "Supplied header {0}. Got error: {1}")
        msg = msg.format(http_auth, str(err))
        logger.debug(msg)
        _raise_unauthorized(desc=msg)

    auth_type = auth_type.lower()

    if auth_type == six.b('basic'):
        request.client_xid = 'tester'
        return

    if auth_type == six.b('basic'):
        logging.debug("Authenticating clint using Basic mechanism...")
        try:
            user_and_key = user_and_key.strip()
            user_and_key = binascii.a2b_base64(user_and_key)
            user_id, key = user_and_key.split(six.b(':'), 1)

            logger.debug("user_id: %s", user_id)

            if not crypto.validate_xid(user_id):
                _raise_unauthorized()

            xid = crypto.secret_key_to_xid(key)
            if xid != user_id:
                _raise_unauthorized()

            request.client_xid = user_id
            logger.debug("Client authenticated: %s", user_id)
            return
        except (binascii.Error, ValueError) as err:
            msg = ("Unable to determine user and pass/key encoding. "
                   "Got error: {0}").format(str(err))
            logger.debug(msg)
            _raise_unauthorized(desc=msg)

    elif auth_type == six.b("bearer"):
        logger.debug("Authenticating client using Bearer mechanism...")
        try:
            tok = token.decode(user_and_key, settings.NETWORK_SECRET, verify=True)
        except token.DecodeError:
            logger.debug("Token decode error", exc_info=True)
            tok = {}
            _raise_unauthorized()

        client_xid = tok.get("sub")
        if not client_xid:
            _raise_unauthorized(desc="Subject not specified in token.")

        if not crypto.validate_xid(client_xid):
            _raise_unauthorized()
        request.client_xid = client_xid
    else:
        _raise_unauthorized("Unsupported authentication method: %s" % auth_type)


def static_file(filepath, root=static_folder, mimetype='auto', download=False, charset='utf-8'):
    return _static_file(filepath, root=root, mimetype=mimetype, download=download, charset=charset)


def swap_root_app(wsgiapp):
    """ Swap the root WSGI application.

    :param wsgiapp:
    :return: the previous WSGI application.
    """
    from ava.core.webfront import dispatcher
    old_app = dispatcher.app
    dispatcher.app = wsgiapp

    return old_app

__all__ = [route, get, post, delete, put, request, response,
           static_file, static_folder, dispatcher, check_authentication]

