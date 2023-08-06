# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import logging
import sys


logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
rootlogger = logging.getLogger()
baselogger = rootlogger.getChild('crosservice')