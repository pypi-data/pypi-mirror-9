# -*- coding: utf-8 -*-
from __future__ import print_function, absolute_import
import struct


# region Sockets
def send_msg(sock, msg):
    if hasattr(msg, 'dump') and callable(msg.dump):
        msg = msg.dump()
    # Prefix each message with a 4-byte length (network byte order)
    # noinspection PyAugmentAssignment
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)


def recv_msg(sock):
    # Read message length and unpack it into an integer
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
