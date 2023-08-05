# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
# @formatter:off
from gevent import monkey
monkey.patch_all()
# @formatter:on
import pickle
from crosservice.log import baselogger
import sys

from gevent import socket

from crosservice.handlers import Result
from crosservice.utils import send_msg, recv_msg


logger = baselogger.getChild('client')


class Client(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send(self, signal, data):
        log = logger.getChild(signal)
        _socket = socket.create_connection((self.host, int(self.port)))
        log.debug("Data: {0}".format(data))
        msg = {'signal': signal, 'data': data}
        msg = pickle.dumps(msg)
        send_msg(_socket, msg)
        response = recv_msg(_socket)
        _socket.close()
        response = Result.load(response)
        if not response:
            log.error(response.error)
        return response


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'test':
        client = Client('127.0.0.1', 1234)
        res = client.send('test', {'a': "lol"})
        assert res.a == 'lol'