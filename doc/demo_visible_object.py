# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Friday, 13 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


import logging
import sys
import datetime
import json

sys.path.append('..')

from unicum import VisibleObject, VisibleAttributeList, VisibleObjectList, VisibleDataRange, UnicumJSONEncoder

logging.basicConfig()


class Person(VisibleObject):

    def __init__(self, name=''):
        super(Person, self).__init__(name)
        self._age_ = 0


class Student(Person):
    pass


class StudentList(VisibleAttributeList):
    def __init__(self, iterable=None, object_type=Student,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(VisibleAttributeList, self).__init__(iterable, object_type, value_types)


class Class(VisibleObject):
    def __init__(self, name=''):
        super(Class, self).__init__(name)
        self._students_ = StudentList()


class Teacher(Person):
    pass


class TeacherList(VisibleAttributeList):
    def __init__(self, iterable=None, object_type=Teacher,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(VisibleAttributeList, self).__init__(iterable, object_type, value_types)


class ClassRoom(VisibleObject):
    pass


class ClassRoomList(VisibleAttributeList):
    def __init__(self, iterable=None, object_type=ClassRoom,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(VisibleAttributeList, self).__init__(iterable, object_type, value_types)


class Lesson(VisibleObject):

    def __init__(self):
        super(Lesson, self).__init__()
        self._subject_ = ''
        self._teacher_ = Teacher()
        self._class_room_ = ClassRoom()
        self._class_ = Class()
        self._day_ = 'Monday'
        self._time_ = '8:30'
        self._hour_ = 1


class Schedule(VisibleAttributeList):
    def __init__(self, iterable=None, object_type=Lesson,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(VisibleAttributeList, self).__init__(iterable, object_type, value_types)


class School(VisibleObject):

    def __init__(self):
        super(School, self).__init__()
        self._teachers_ = TeacherList()
        self._students_ = StudentList()
        self._class_rooms_ = ClassRoomList()
        self._schedule_ = Schedule()


if __name__=='__main__':

    School().register()
    School().modify_object('Teachers', TeacherList(('Mr. Logan', 'Mrs. Smith')).register())
    School().modify_object('Students', StudentList(('Tom','Ben','Luisa','Peter','Paul','Mary')).register())
    School().modify_object('ClassRooms', ClassRoomList(('Room 1','Room 2','Hall')).register())

    Class('FreshMen').register().modify_object('Students', School().get_property('Students')[:3])
    Class('Senior').register().modify_object('Students', School().get_property('Students')[3:])

    School().get_property('Schedule').append(
        Lesson.create(Subject='Math', Teacher='Mr. Logan', Class='FreshMen', ClassRoom='Room 1', Time='8:30'))
    School().get_property('Schedule').append(
        Lesson.create(Subject='Physics', Teacher='Mr. Logan', Class='Senior', ClassRoom='Room 2', Time='10:15'))
    School().get_property('Schedule').append(
        Lesson.create(Subject='Math', Teacher='Mr. Logan', Class='Senior', ClassRoom='Room 2', Time='12:00'))
    School().get_property('Schedule').append(
        Lesson.create(Subject='History', Teacher='Mrs. Smith', Class='Senior', ClassRoom='Room 2', Time='8:30'))
    School().get_property('Schedule').append(
        Lesson.create(Subject='Sports', Teacher='Mrs. Smith', Class='FreshMen', ClassRoom='Hall', Time='10:15'))
    School().get_property('Schedule').append(
        Lesson.create(Subject='History', Teacher='Mrs. Smith', Class='FreshMen', ClassRoom='Room 1', Time='12:00'))

    print(School().to_json(all_properties_flag=True, indent=2))

    #
