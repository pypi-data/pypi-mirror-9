# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import

import os

from .server import start_server


LISTEN_HOST = os.environ.get('CROSSERVICE_LISTEN_HOST', '127.0.0.1')
LISTEN_PORT = os.environ.get('CROSSERVICE_LISTEN_PORT', 12345)
SPAWN = os.environ.get('CROSSERVICE_SPAWN', 2000)

if __name__ == "__main__":
    start_server(LISTEN_HOST, LISTEN_PORT, SPAWN)