# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
import struct

from .constants import VERSION
from .log import baselogger


logger = baselogger.getChild('utils')


# region Sockets
def send_msg(sock, msg):
    if hasattr(msg, 'dump') and callable(msg.dump):
        msg = msg.dump()
    msglen = len(msg)
    msg_ = struct.pack('>cHI', str('v'), VERSION, msglen)
    msg = msg_ + msg
    sock.sendall(msg)


def recv_msg(sock):
    log = logger.getChild('recv_msg')
    # Read message length and unpack it into an integer
    _ = recvall(sock, 1)

    raw_version = recvall(sock, 2)
    version = struct.unpack('>H', raw_version)[0]

    if version != VERSION:
        log.critical(
            'Version missmatch. Clinent version: {0}, server: {1}'.format(
                version, VERSION
            )
        )
        return None

    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None

    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)


def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

# endregion
