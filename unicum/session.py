# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


import warnings

from inspect import getargspec, ismethod
from logging import getLogger
from traceback import format_exc
from os import linesep

from multiprocessing import Process, Queue


class SessionHandler(object):

    _types = {
        'number': int,
        'year': int,
        'month': int,
        'day': int,
        'int': int,
        'long': int,
        'float': float,
        'value': float,
        'str': str,
        'string': str,
        'name': str,
        'bool': bool,
        'flag': bool,
        'variant': (lambda x: x)
    }

    def __init__(self, pkg_name='unicum', cls_name='VisibleObject', cast_types={}):
        """ api session handler for multiprocessing sessions

        :param pkg_name: module containing relevant classes
        :param cls_name: default class (inherited from unicum.VisibleObject)
        :param types: additional dict of types to cast arguments

        Standard type conversion is following a naming convention.
        So if an arguments ends with `int` the value will be casted with the type :code:`int`
        given as value to the key `int` in **types**.

        Same with `number`, `year`, `month`, `day` and `long`.
        Similar we cast `float` and `value` to a :code:`float`,
        `string`, `str` and `name` to a :code:`str` as well as
        `bool` and  `flag` to :code:`bool`

        Anything ending with `variant` would be ignored.

        And finally, the value of `cls` will be replaced by an attribute of **pkg_name** of the same name
        and the value of `self` will be replaced by an **cls_name** instance.

        """

        self._pkg_name = pkg_name
        self._cls_name = cls_name
        self._cast_types = dict()
        self._cast_types.update(self.__class__._types)
        self._cast_types.update(cast_types)

        # initialize session dict
        self._sessions = dict()

    def start_session(self, session_id):
        """ starts a session with given session_id """

        if session_id in self._sessions:
            raise ValueError("Session of id %s exists already." % session_id)

        task_queue = Queue()
        result_queue = Queue()
        args = task_queue, result_queue, self._pkg_name, self._cls_name, self._cast_types

        session = Process(target=self._run, name=session_id, args=args)
        self._sessions[session_id] = session, task_queue, result_queue
        session.start()
        return session_id

    def validate_session(self, session_id):
        """ checks wether a session with given session id exists """
        return session_id in self._sessions

    def call_session(self, session_id, func='', kwargs={}):
        """ calls the session and makes a function call with kwargs (which will be casted accordingly) """
        if session_id not in self._sessions:
            return 'session %s does not exists.' % session_id

        # worker job
        session, task_queue, result_queue = self._sessions.get(session_id)

        task = func, kwargs
        task_queue.put(task)
        result = result_queue.get()
        return result

    def stop_session(self, session_id):
        """ closes a session with given session_id """
        if session_id not in self._sessions:
            raise ValueError("Session id %s not found." % session_id)
        session, task_queue, result_queue = self._sessions.pop(session_id)
        session.terminate()
        session.join()
        return 'session %s closed.' % session_id

    @staticmethod
    def _run(task, result, pkg_name, cls_name, types):
        """ run session loop """

        _module = __import__(pkg_name)
        _class = getattr(_module, cls_name)
        _types = types
        _types['cls'] = (lambda c: getattr(_module, c)),
        _types['self'] = _class,

        def _cast(name, value):
            name = str(name).strip().lower()
            names = [n for n in list(_types.keys()) if name.endswith(n)]
            names.append('variant')
            _type = _types.get(names[0])
            return _type(value)

        def _gather_func_kwargs(func, kwargs):
            """ gather func arguments by first argument name

            :param func:
            :param kwargs:
            :return:

            tries to distinguish class, static and instance methods by analysing first=kwargs[0]
                class method if first is attribute of Session._module and subclass of Session._class
                instance method else
            no chance for static method implemented

            """
            keys = sorted(kwargs.keys())
            values = list(kwargs[k] for k in keys)
            first = values[0]
            # gather instance method or class method
            if not hasattr(_module, first):
                obj = _class(first)
            else:
                obj = getattr(_module, first)
                cm = _class.__name__, _module.__name__
                msg = 'first argument must either be subclass of %s or not attribute of %s' % cm
                raise TypeError(msg)

            if not hasattr(obj, func):
                raise AttributeError('func %s must be method of %s' % (func, obj))
            func = getattr(obj, func)
            if not ismethod(func):
                raise AttributeError('func %s must be method of %s' % (func, obj))

            args = getargspec(func).args
            kwargs = dict(list(zip(args, list(kwargs.values()))))

            return kwargs

        def _func(func, kwargs):
            if all(k.startswith('arg') for k in list(kwargs.keys())):
                kwargs = _gather_func_kwargs(func, kwargs)

            # use cls resp. self
            _cls = getattr(_module, kwargs.pop('cls', ''), _class)
            _self = kwargs.pop('self', '')
            if _self:
                if _self in list(_cls.keys()):
                    obj = _cls(_self)
                else:
                    raise KeyError('Object %s does not exists.' % _self)
            else:
                obj = _cls
            func = obj._to_visible(func).strip('_')
            func = getattr(obj, func)
            return obj, func, kwargs

        def _prepickle(item):
            if isinstance(item, dict):
                keys = _prepickle(list(item.keys()))
                values = _prepickle(list(item.values()))
                item = dict(list(zip(keys, values)))
            elif isinstance(item, list):
                item = [_prepickle(i) for i in item]
            elif isinstance(item, tuple):
                item = (_prepickle(i) for i in item)
            elif isinstance(item, (bool, int, float, str, type(None))):
                pass
            else:
                item = str(item)
            return item

        while True:
            # get from task queue
            this_task = task.get()
            try:
                # pick task and build obj, func and kwargs
                func_name, kwargs = this_task
                obj, func, kwargs = _func(func_name, dict(list(kwargs.items())))
                # cast values by cast function
                kwargs = dict((k, _cast(k, v)) for k, v in list(kwargs.items()))
                # do job
                nice = (lambda k: str(k[0]) + '=' + repr(k[1]))
                msg = 'call %s.%s(%s)' % (repr(obj), func_name, ', '.join(map(nice, list(kwargs.items()))))
                # print msg
                getLogger().debug(msg)
                value = func(**kwargs)
                # prepare to pickle
                # value = value if isinstance(value, (bool, int, long, float, str, list, dict)) else str(value)
                value = _prepickle(value)
            except Exception as e:
                value = e.__class__.__name__ + ': ' + str(e)
                warnings.warn('%s was raised.' % value)
                getLogger().error(format_exc())

            # send to result queue
            result.put(value)
