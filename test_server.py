"""
UnitTests for the RALF in order to send objects to ralf
"""
import os
import psutil

from json import loads
from thread import start_new_thread
from unittest import TestCase, main

import requests

from unicum.server import Server
from unicum.server import Session

from unicum import VisibleObject


class TestVisibleObject(VisibleObject):

    def __init__(self, *args, **kwargs):
        super(TestVisibleObject, self).__init__(*args, **kwargs)
        self._folder_ = ''
        self._float_ = 0.


class TestSession(Session):
    import test_server
    _module = test_server
    _class = _module.TestVisibleObject


def terminate_python():
    """ terminate any other python process """
    for process in psutil.process_iter():
        pid = os.getpid()
        if process.name() == 'Python' and not process.pid == pid:
            process.terminate()


class RestAPITests(TestCase):
    """ Server unit tests """

    def setUp(self):
        self.host = '127.0.0.1'
        self.port = 2699

    def start_server(self):
        terminate_python()
        url = "http://" + self.host + ":" + str(self.port) + "/"
        # print 'start server at url %s with module %s' % (url, str(self.module))
        start_new_thread(Server(TestSession).run, (self.host, self.port))
        return url

    def stop_server(self, url):
        requests.get(url=url + 'stop')
        terminate_python()


class UnicumTests(RestAPITests):
    """ Object unit tests """

    def test_session(self):
        # start server
        server_url = self.start_server()

        # open session
        get_trans = requests.get(url=server_url)
        session_url = server_url + get_trans.content
        self.assertEqual(get_trans.status_code, 200)

        # close session
        post_obj = requests.delete(url=session_url)
        self.assertEqual(post_obj.status_code, 200)

        # stop server
        self.stop_server(server_url)

    def test_create(self):
        # start server
        server_url = self.start_server()
        name = 'my_object'
        folder = 'my_folder'

        # open session
        get_trans = requests.get(url=server_url)
        self.assertEqual(get_trans.status_code, 200)
        session_url = server_url + get_trans.content

        # call create
        url = session_url + '/create'
        par = {'name': name,
               'register_flag': True}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, name)

        url = session_url + '/modify_object'
        par = {'self': name,
               'property_name': 'Folder',
               'property_value_variant': folder}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, name)

        url = session_url + '/get_property'
        par = {'self': name,
               'property_name': 'Name'}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, name)

        url = session_url + '/get_property'
        par = {'self': name,
               'property_name': 'Folder'}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, folder)

        url = session_url + '/to_serializable'
        par = {'self': name}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(loads(call_res.text)['Name'], name)
        self.assertEqual(loads(call_res.text)['Folder'], folder)

        # close session
        post_obj = requests.delete(url=session_url)
        self.assertEqual(post_obj.status_code, 200)

        # stop server
        self.stop_server(server_url)

    def test_create_with_args(self):
        # start server
        server_url = self.start_server()
        name = 'my_object'
        folder = 'my_folder'

        # open session
        get_trans = requests.get(url=server_url)
        self.assertEqual(get_trans.status_code, 200)
        session_url = server_url + get_trans.content

        # call create
        url = session_url + '/create'
        par = {'arg0': 'TestVisibleObject',
               'arg1': name,
               'arg2': True}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, name)

        url = session_url + '/modify_object'
        par = {'arg0': name,
               'arg1': 'Folder',
               'arg2': folder}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, name)

        url = session_url + '/get_property'
        par = {'arg0': name,
               'arg1': 'Name'}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, name)

        url = session_url + '/get_property'
        par = {'arg0': name,
               'arg1': 'Folder'}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(call_res.text, folder)

        url = session_url + '/to_serializable'
        par = {'arg0': name}
        call_res = requests.get(url=url, params=par)
        self.assertEqual(call_res.status_code, 200)
        self.assertEqual(loads(call_res.text)['Name'], name)
        self.assertEqual(loads(call_res.text)['Folder'], folder)

        # close session
        post_obj = requests.delete(url=session_url)
        self.assertEqual(post_obj.status_code, 200)

        # stop server
        self.stop_server(server_url)

if __name__ == '__main__':
    main(verbosity=2)
