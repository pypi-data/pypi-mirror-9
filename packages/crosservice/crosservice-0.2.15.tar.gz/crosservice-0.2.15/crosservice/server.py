# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
# @formatter:off
from gevent import monkey
monkey.patch_all()
# @formatter:on
import pickle
from .handlers import Handlers, Result
import logging

from gevent.server import StreamServer

from .utils import recv_msg, send_msg

log = logging.getLogger(__name__)


def handler(socket, address):
    log.info("Request from {0}".format(address))
    message = recv_msg(socket)
    message = pickle.loads(message)
    res = Result()

    # Check for all required keys
    if not ('data' in message and 'signal' in message):
        log.error("Incomplete message, passed: {0}".format(message.keys()))
        res.error = 'Missed data or signal'

        send_msg(socket, res)
        return

    signal = message['signal']
    data = message['data']
    if not data:
        data = {}

    log.debug("Signal {0} received".format(signal))
    # Trying to execute action's handler
    if signal in Handlers:
        h = Handlers[signal]
        """:type: .handlers.Handler"""
        log.info(
            "Using `{0}` as handler for signal `{1}`".format(
                h.name, signal
            )
        )
        res = h(**data)
    else:
        log.warning("No handler for signal `{0}`".format(signal))
        res.error = "No handler for signal {0}".format(signal)

    send_msg(socket, res)


def start_server(host, port, spawn):
    log.info(
        "Start listening at {host}:{port} with spawn value {spawn}".format(
            host=host, port=port, spawn=spawn
        ))
    server = StreamServer((host, int(port)), handle=handler, spawn=spawn)
    server.serve_forever()
