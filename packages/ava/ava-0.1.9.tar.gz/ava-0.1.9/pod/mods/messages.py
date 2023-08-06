# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import logging
import bottle
from ava.spi.webfront import dispatcher, route,  request, check_authentication


logger = logging.getLogger(__name__)

app = bottle.Bottle()
app.add_hook('before_request', check_authentication)


@app.post('/')
def on_post_message():
    """ Invoked when others want to send this agent messages.

    :return:
    """
    if request.json:
        logger.debug("Message received: %s", request.json)


@app.get("/")
def on_get_message():
    logger.debug("Getting messages for %s", request.client_xid)


dispatcher.mount('/messages', app)
logger.debug("Mounted message store to webfront at /messages.")