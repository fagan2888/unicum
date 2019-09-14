# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
#
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Friday, 13 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


from datetime import datetime
from hashlib import md5

from flask import Flask, request, jsonify
from flask.helpers import make_response

from unicum import SessionHandler, VisibleObject


class DemoServer(Flask):
    """ restful api class """

    def __init__(self, session_handler=SessionHandler(), *args, **kwargs):

        # store session properties
        self._session_handler = session_handler

        # initialize Flask
        kwargs['import_name'] = kwargs.get('import_name', 'unicum_web_service')
        super(DemoServer, self).__init__(*args, **kwargs)
        self.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

        # initialize url routes/rules to manage session
        self.add_url_rule('/', view_func=self._start_session, methods=["GET"])
        self.add_url_rule('/<session_id>', view_func=self._validate_session, methods=["GET"])
        self.add_url_rule('/<session_id>', view_func=self._stop_session, methods=["DELETE"])
        self.add_url_rule('/<session_id>/<func>', view_func=self._call_session, methods=["GET", "POST"])

    # manage sessions
    def _start_session(self):
        """ starts a session """
        assert request.method == 'GET'

        hash_str = str(request.remote_addr) + str(datetime.now())
        session_id = md5(hash_str.encode()).hexdigest()

        session_id = self._session_handler.start_session(session_id)
        return make_response(session_id, 200)

    def _validate_session(self, session_id):
        result = self._session_handler.validate_session(session_id)
        return make_response(jsonify(result), 200)

    def _call_session(self, session_id, func=''):
        """ create object """

        assert request.method in ('GET', 'POST')
        if session_id not in request.base_url:
            return make_response(jsonify('session id %s does not match.' % session_id), 500)

        # get key word arguments
        kwargs = dict()
        if request.method == 'GET':
            kwargs = request.args
        elif request.method == 'POST':
            kwargs = request.get_json(force=True)

        result = self._session_handler.call_session(session_id, func, kwargs)

        if isinstance(result, (bool, int, float, str)):
            result = str(result)
        else:
            result = jsonify(result)

        return make_response(result)

    def _stop_session(self, session_id):
        """ closes a session """
        assert request.method in ('DELETE', 'GET')
        assert session_id in request.base_url

        result = self._session_handler.stop_session(session_id)
        return make_response(jsonify(result), 200)

    # manage server
    def _shutdown(self):
        for session_id in self._sessions:
            self._session_handler.stop_session(session_id)

        request.environ.get('werkzeug.server.shutdown')()
        res = 'shutting down...'
        return make_response(jsonify(res))


class DemoObject(VisibleObject):
    def __init__(self, *args, **kwargs):
        super(DemoObject, self).__init__(*args, **kwargs)
        self._folder_ = ''
        self._float_ = 0.


if __name__ == '__main__':
    import requests
    from _thread import start_new_thread

    ################################################
    # start server at http://127.0.0.1:64001
    ################################################

    url, port = '127.0.0.1', '64001'
    start_new_thread(DemoServer(SessionHandler('demo_server', 'DemoObject')).run, (url, port))

    ################################################
    # start session
    ################################################

    base_url = 'http://%s:%s/' % (url, port)
    session_id = requests.get(url=base_url)

    ################################################
    # call session
    ################################################

    # ----------------------------------------------
    # create object
    # ----------------------------------------------

    url = base_url + session_id.text
    name = 'MyName'
    folder = 'MyFolder'
    res = requests.get(
        url=url + '/create',
        params={
            'name': name,
            'register_flag': True
        })
    assert res.text == name

    # ----------------------------------------------
    # modify object
    # ----------------------------------------------

    res = requests.get(
        url=url + '/modify_object',
        params={
            'self': name,
            'property_name': 'Folder',
            'property_value_variant': folder
        })
    assert res.text == name

    res = requests.get(
        url=url + '/modify_object',
        params={
            'self': name,
            'property_name': 'Float',
            'property_value_variant': 123.321
        })
    assert res.text == name

    # ----------------------------------------------
    # get properties
    # ----------------------------------------------

    res = requests.get(
        url=url + '/get_property',
        params={
            'self': name,
            'property_name': 'Class'
        })
    assert res.text == 'DemoObject'

    res = requests.get(
        url=url + '/get_property',
        params={
            'self': name,
            'property_name': 'Folder'
        })
    assert res.text == folder

    res = requests.get(
        url=url + '/get_property',
        params={
            'self': name,
            'property_name': 'Float'
        })
    assert abs(float(res.text) - 123.321) < 1e-10

    ################################################
    # close session
    ################################################

    session_id = requests.delete(url=url)

    ################################################
    # stop server
    ################################################

    requests.delete(url=base_url)
