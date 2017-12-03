import datetime
import hashlib
import warnings


from multiprocessing import Process, Queue
from inspect import getargspec, ismethod
from logging import getLogger

from flask import Flask, request, jsonify
from flask.helpers import make_response

SERVER_NAME = 'core-server'


class Session(object):
    """ api session to handle request in multiprocessing """
    import unicum

    _module = unicum
    _class = _module.VisibleObject
    _default_key_start = 'arg'
    _types = {
        'cls': (lambda c: getattr(_module, c)),
        'self': _class,
        'number': int,
        'year': int,
        'month': int,
        'day': int,
        'int': int,
        'long': long,
        'float': float,
        'value': float,
        'str': str,
        'name': str,
        'bool': bool,
        'flag': bool,
        'variant': (lambda x: x)
    }

    def run(self, task, result):
        """ run session loop

        :param task: queue for tasks tuples (func, kwargs)
        :param result:  queue for return values = self.func(**kwargs)
        :return:
        """

        def _cast(cls, name, value):
            name = str(name).strip().lower()
            names = [n for n in cls._types.keys() if name.endswith(n)]
            names.append('variant')
            _type = cls._types.get(names[0])
            return _type(value)

        def _gather_func_kwargs(cls, func, kwargs):
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
            if not hasattr(cls._module, first):
                obj = cls._class(first)
            else:
                obj = getattr(cls._module, first)
                cm = cls._class.__name__, cls._module.__name__
                msg = 'first argument must either be subclass of %s or not attribute of %s' %cm
                assert issubclass(obj, Session._class), msg

            msg = 'func %s must be method of %s' % (func, obj)
            assert hasattr(obj, func), msg
            func = getattr(obj, func)
            assert ismethod(func), msg

            args = getargspec(func).args
            kwargs = dict(zip(args, kwargs.values()))

            return kwargs

        def _func(cls, func, kwargs):
            if all(k.startswith(cls._default_key_start) for k in kwargs.keys()):
                kwargs = _gather_func_kwargs(cls, func, kwargs)

            # use cls resp. self
            _cls = getattr(cls._module, kwargs.pop('cls', ''), cls._class)
            _self = kwargs.pop('self', '')
            if _self:
                if _self in _cls.keys():
                    obj = _cls(_self)
                else:
                    raise KeyError('Object %s does not exists.' %_self)
            else:
                obj = _cls
            func = getattr(obj, func)
            return obj, func, kwargs

        while True:
            # get from task queue
            this_task = task.get()
            try:
                # pick task and build obj, func and kwargs
                func_name, kwargs = this_task
                obj, func, kwargs = _func(self.__class__, func_name, dict(kwargs.items()))
                # cast values by cast function
                kwargs = dict((k, _cast(self.__class__, k, v)) for k, v in kwargs.items())
                # do job
                nice = (lambda k: str(k[0]) + '=' + repr(k[1]))
                msg = 'call %s.%s(%s)' % (repr(obj), func_name, ', '.join(map(nice, kwargs.items())))
                # print msg
                getLogger(SERVER_NAME).debug(msg)
                value = func(**kwargs)
                # prepare to pickle
                value = value if isinstance(value, (bool, int, long, float, str, list, dict)) else str(value)
            except Exception as e:
                value = e.__class__.__name__ + ': ' + str(e.message.encode('ascii'))
                warnings.warn('%s was raised.' % value)
            # send to result queue
            result.put(value)


class Server(Flask):
    """ restful api class """

    def __init__(self, session=Session, *args, **kwargs):

        # store session class
        self._session_class = session

        # initialize Flask
        kwargs['import_name'] = kwargs.get('import_name', SERVER_NAME)
        super(Server, self).__init__(*args, **kwargs)
        self.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        # initialize session dict
        self._sessions = dict()

        # initialize url routes/rules to manage session
        self.add_url_rule('/', view_func=self._start_session, methods=["GET"])
        self.add_url_rule('/<session_id>', view_func=self._validate_session, methods=["GET"])
        self.add_url_rule('/<session_id>', view_func=self._stop_session, methods=["DELETE"])
        self.add_url_rule('/<session_id>/<func>', view_func=self._call_session, methods=["GET", "POST"])

    # manage sessions
    def _start_session(self):
        """ starts a session """
        assert request.method == 'GET'

        hash_str = str(request.remote_addr) + str(datetime.datetime.now())
        session_id = hashlib.md5(hash_str).hexdigest()
        assert session_id not in self._sessions

        task_queue = Queue()
        result_queue = Queue()
        args = task_queue, result_queue
        api_session = self._session_class()
        session = Process(target=api_session.run, name=session_id, args=args)
        self._sessions[session_id] = session, task_queue, result_queue
        session.start()

        return make_response(session_id, 200)

    def _validate_session(self, session_id):
        result = session_id in self._sessions
        return make_response(jsonify(result), 200)

    def _call_session(self, session_id, func=''):
        """ create object """

        assert request.method in ('GET', 'POST')
        if session_id not in self._sessions:
            return make_response(jsonify('session %s does not exists.' % session_id), 500)
        if session_id not in request.base_url:
            return make_response(jsonify('session id %s does not match.' % session_id), 500)

        # get key word arguments
        kwargs = dict()
        if request.method == 'GET':
            kwargs = request.args
        elif request.method == 'POST':
            kwargs = request.get_json(force=True)

        # worker job
        session, task_queue, result_queue = self._sessions.get(session_id)

        task = func, kwargs
        task_queue.put(task)
        result = result_queue.get()

        if not isinstance(result, (bool, int, long, float, str, unicode)):
            result = jsonify(result)

        return make_response(result, 200)

    def _stop_session(self, session_id):
        """ closes a session """
        assert request.method in ('DELETE', 'GET')
        assert session_id in self._sessions
        assert session_id in request.base_url

        result = self._shutdown_session(session_id)
        return make_response(jsonify(result), 200)

    def _shutdown_session(self, session_id):
        session, task, result = self._sessions.pop(session_id)
        session.terminate()
        session.join()
        return 'session %s closed.' % session_id

    # manage server
    def _shutdown(self):
        for session_id in self._sessions:
            self._shutdown_session(session_id)

        request.environ.get('werkzeug.server.shutdown')()
        res = 'shutting down...'
        return make_response(jsonify(res))


if __name__ == '__main__':
    Server().run('127.0.0.1', 2699)
