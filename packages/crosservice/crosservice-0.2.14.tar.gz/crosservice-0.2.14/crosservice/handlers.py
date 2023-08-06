# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function, absolute_import
import pickle
import inspect

from gevent.lock import RLock
import six

from . import constants
from .log import baselogger


logger = baselogger.getChild('handlers')


# region HandlersStorage
class HandlersStorage(object):
    _lock = RLock()
    _data = {}
    log = logger.getChild('HandlersStorage')

    def __setitem__(self, key, value):
        self._lock.acquire()
        try:
            value = value()
            if key in self._data:
                self.log.warning(
                    'Overload of handler for signal {0}: {1} -> {2}'.format(
                        key, self._data[key].name, value.name
                    )
                )
            else:
                self._data[key] = value
        finally:
            self._lock.release()

    def __getitem__(self, item):
        self._lock.acquire()
        data = None
        try:
            if item in self._data:
                data = self._data[item]
        finally:
            self._lock.release()
        return data

    def __delitem__(self, key):
        self._lock.acquire()
        try:
            if key in self._data:
                del self._data[key]
        finally:
            self._lock.release()

    def __contains__(self, item):
        return item in self._data

    def items(self):
        return self._data.items()

    def keys(self):
        return self._data.keys()

    def values(self):
        return self._data.values()


Handlers = HandlersStorage()
# endregion


# region Result
class BaseResult(object):
    _status = False
    """:type: bool"""
    _error = None
    """:type: str or unicode"""
    _result = {}
    """:type: dict"""

    def __init__(self, status=None, result=None, error=None):
        if status:
            self._status = status

        if result and isinstance(result, dict):
            self._result = result

        if error:
            self._error = error

    def __getattr__(self, item):
        if item in self._result:
            return self._result[item]
        raise AttributeError()

    def __setitem__(self, key, value):
        if not self._result:
            self.result = {}

        self._result[key] = value

    def __contains__(self, item):
        if item == 'error' and self.error:
            return True

        return item in self._result

    def __iter__(self):
        for k, v in self._result.items():
            yield k, v

    def get_result(self):
        return self._result

    def set_result(self, result):
        self._status = True
        self._result = result

    result = property(get_result, set_result)

    def get_error(self):
        return self._error

    def set_error(self, error):
        self._status = False
        self._error = error

    error = property(get_error, set_error)

    def __nonzero__(self):
        return self._status

    def dict(self):
        return self._result

    def keys(self):
        return self._result.keys()

    def values(self):
        return self._result.values()

    def items(self):
        return self._result.items()

    def dump(self):
        return pickle.dumps(self)

    @classmethod
    def load(cls, data):
        return pickle.loads(data)


class Result(BaseResult):
    pass
# endregion


# region Handlers
class HandlerMetaClass(type):
    def __new__(mcs, name, bases, namespace):
        cls = super(HandlerMetaClass, mcs).__new__(mcs, name, bases, namespace)

        if name != 'BaseHandler' and \
                not ('abstract' in cls.__dict__ and getattr(cls, 'abstract')):
            cls.name = "%s.%s" % (namespace['__module__'], name)
            assert cls.signal, \
                "Signal must be specified at %s" % cls.name

            cls.init()

            Handlers[cls.signal] = cls

        return cls


@six.add_metaclass(HandlerMetaClass)
class BaseHandler(object):
    signal = None

    abstract = False
    _logger = None
    result = None
    _result_class = Result
    required_data = None
    exception_action = constants.EX_RESULT_ERR

    def __init__(self):
        self.result = self._result_class()
        self.__name__ = self.__class__.__name__

    @classmethod
    def init(cls):
        cls._logger = baselogger.getChild(cls.__name__)

    # region logging
    def _exception(self, message):
        self._logger.exception(message)

    def _critical(self, message):
        self._logger.critical(message)

    def _error(self, message):
        self._logger.error(message)

    def _warning(self, message):
        self._logger.warning(message)

    def _info(self, message):
        self._logger.info(message)

    def _debug(self, message):
        self._logger.debug(message)
    # endregion

    def __call__(self, **kwargs):
        err = False
        if self.required_data:
            err = self._check_required_data(kwargs)

        if not err:
            # Clean passed data
            args, _, varkw, _ = inspect.getargspec(self.run)
            # If function not accepts **kwargs
            if not varkw:
                # Drop all non-acceptable keys
                kwargs_keys = kwargs.keys()
                for k in kwargs_keys:
                    if k not in args:
                        self._debug("Drop unacceptable key {0}".format(k))
                        kwargs.pop(k)

            # Execute handler's run-method
            try:
                self.run(**kwargs)
            except Exception as e:
                self._exception(e)
                self._proccess_exception(e)

        return self.result

    def _proccess_exception(self, e):
        if self.exception_action == constants.EX_RAISE:
            raise e
        else:
            self.result.error = e

    def _check_required_data(self, input_data):
        input_keys = input_data.keys()
        err = False
        self.result.missed_keys = []

        for k in self.required_data:
            if k not in input_keys:
                err = True
                self._error('Missed key {0}'.format(k))
                self.result.missed_keys.append(k)

        if err:
            self.result.error = 'Missed data'
        else:
            del self.result.missed_keys

        return err

    def run(self, **kwargs):
        raise NotImplementedError()
# endregion
