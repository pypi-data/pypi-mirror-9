# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, unicode_literals


import logging
from ava.spi.webfront import post, request


logger = logging.getLogger(__name__)


@post("/messages")
def on_message():
    """ Invoked when others want to send this agent messages.

    :return:
    """
    if request.json:
        logger.debug("Message received: %s", request.json)

