Gevent powered cross service communication tool
===============================================

This tool is aimed to provide simple and customizable interface for
communication between different services over sockets. **No encryption yet.**

Simple example:
---------------

Client::

    from crosservice.signals import BaseSignal

    class PingSignal(BaseSignal):
        _host = '127.0.0.1'
        _port = 5555
        signal = 'ping'
        expect_data = ['time']

    if __name__ == '__main__':
        ping = PingSignal({'foo': 'bar'})
        if ping.result:
            print ping.result.foo, ':', ping.result.time
        else:
            print "Error: ", ping.result.error


Server::

    from crosservice.server import start_server
    from crosservice.handlers import BaseHandler
    import time

    class PingHandler(BaseHandler):
        signal = 'ping'
        required_data = ['foo']

        def run(self, foo):
            if foo == 'bar':
                foo = 'received at'
                self.result.foo = foo
                self.result.time = time.time()
            else:
                self.result.error = 'Bad foo!'

    if __name__ == '__main__':
        start_server('127.0.0.1', 5555, 1000)
