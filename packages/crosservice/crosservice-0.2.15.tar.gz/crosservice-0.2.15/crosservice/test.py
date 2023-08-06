# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
# @formatter:off
from gevent import monkey
import time
monkey.patch_all()
# @formatter:on
from crosservice.server import start_server
from multiprocessing.process import Process
from crosservice.signals import BaseSignal
from crosservice.client import Client
import unittest
from crosservice.handlers import BaseHandler


# TODO: Test missed data events

# region Signals and handlers for testing
class Signal(BaseSignal):
    _host = '127.0.0.1'
    _port = 1234


class ABSHandler(BaseHandler):
    abstract = True


class TestHandler(ABSHandler):
    signal = 'test'

    def run(self, *args, **kwargs):
        self.result.result = kwargs


class TestSignal(Signal):
    signal = 'test'


class TestErrorHandler(BaseHandler):
    signal = 'test_error'

    def run(self, *args, **kwargs):
        self.result.error = kwargs


class TestErrorSignal(Signal):
    signal = 'test_error'


# endregion


class MyTestCase(unittest.TestCase):
    def test_success(self):
        signal = TestSignal({'a': 1})
        self.assertTrue(bool(signal.result))
        self.assertEqual(signal.result.a, 1)
        signal.result.a = 2
        self.assertEqual(signal.result.a, 2)
        self.assertTrue('a' in signal.result)
        self.assertFalse('b' in signal.result)

    def test_error(self):
        signal = TestErrorSignal({'a': 2})
        self.assertFalse(bool(signal.result))
        self.assertEqual(signal.result.error, {'a': 2})
        self.assertRaises(AttributeError, lambda: signal.result.a)

    def test_no_handler(self):
        client = Client('127.0.0.1', 1234)
        res = client.send('signal_not_exists', {'a': 1})
        self.assertFalse(bool(res))
        self.assertIn('signal_not_exists', res.error)
        self.assertRaises(AttributeError, lambda: res.a)


if __name__ == '__main__':
    server = Process(target=start_server, args=('127.0.0.1', 1234, 100))
    tests = Process(target=unittest.main)

    server.start()
    tests.start()
    server.join()
    time.sleep(2)
    tests.join()
