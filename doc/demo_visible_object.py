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

sys.path.append('..')
logging.basicConfig()

from unicum import VisibleObject, VisibleAttributeList, VisibleObjectList, VisibleDataRange


class Person(VisibleObject):
    def __init__(self, name=''):
        super(Person, self).__init__(name)
        self._age_ = 0


class Student(Person):
    def __init__(self, name=''):
        super(Student, self).__init__(name)
        self._school_class_ = SchoolClass()


class Teacher(Person):
    pass


class ClassRoom(VisibleObject):
    pass


class StudentList(VisibleAttributeList):
    def __init__(self, iterable=None):
        super(StudentList, self).__init__(iterable, Student)


class TeacherList(VisibleAttributeList):
    def __init__(self, iterable=None):
        super(TeacherList, self).__init__(iterable, Teacher)


class ClassRoomList(VisibleAttributeList):
    def __init__(self, iterable=None):
        super(ClassRoomList, self).__init__(iterable, ClassRoom)


class SchoolClass(VisibleObject):
    def __init__(self, name=''):
        super(SchoolClass, self).__init__(name)
        self._students_ = StudentList()


class Lesson(VisibleObject):
    def __init__(self):
        super(Lesson, self).__init__()
        self._subject_ = ''
        self._teacher_ = Teacher()
        self._class_room_ = ClassRoom()
        self._school_class_ = SchoolClass()
        self._day_ = 'Monday'
        self._time_ = '8:30'
        self._hour_ = 1


class Schedule(VisibleAttributeList):
    def __init__(self, iterable=None, object_type=Lesson,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(Schedule, self).__init__(iterable, object_type, value_types)


class School(VisibleObject):
    def __init__(self):
        super(School, self).__init__()
        self._teachers_ = TeacherList()
        self._students_ = StudentList()
        self._class_rooms_ = ClassRoomList()
        self._schedule_ = Schedule()


if __name__ == '__main__':
    School().register()  # turns School() into an `unicum` class (with only one `unnamed` instance)
    School().modify_object('Schedule', Schedule())  # mark School().Schedule as modified

    # fill the Schedule with Lessons
    School().get_property('Schedule').append(
        Lesson.create(
            Subject='Math',
            Teacher='Mr. Logan',
            SchoolClass='FreshMen',
            ClassRoom='Room 1',
            Time='8:30'
        ))

    School().get_property('Schedule').append(
        Lesson.create(
            Subject='Physics',
            Teacher='Mr. Logan',
            SchoolClass='Senior',
            ClassRoom='Room 2',
            Time='10:15'
        ))

    School().get_property('Schedule').append(
        Lesson.create(
            Subject='Math',
            Teacher='Mr. Logan',
            SchoolClass='Senior',
            ClassRoom='Room 2',
            Time='12:00'
        ))

    School().get_property('Schedule').append(
        Lesson.create(
            Subject='History',
            Teacher='Mrs. Smith',
            SchoolClass='Senior',
            ClassRoom='Room 2',
            Time='8:30'
        ))

    School().get_property('Schedule').append(
        Lesson.create(
            Subject='Sports',
            Teacher='Mrs. Smith',
            SchoolClass='FreshMen',
            ClassRoom='Hall',
            Time='10:15'
        ))

    School().get_property('Schedule').append(
        Lesson.create(
            Subject='History',
            Teacher='Mrs. Smith',
            SchoolClass='FreshMen',
            ClassRoom='Room 1',
            Time='12:00'
        ))

    # fill VisibleAttributeList
    School().modify_object('Teachers', TeacherList(('Mr. Logan', 'Mrs. Smith')).register())
    School().modify_object('Students', StudentList(('Tom', 'Ben', 'Luisa', 'Peter', 'Paul', 'Mary')).register())
    School().modify_object('ClassRooms', ClassRoomList(('Room 1', 'Room 2', 'Hall')).register())

    # give students an assigned class which makes the object tree circular:
    # School().Students[0] in School().Students[0].SchoolClass.Students
    # (hence, the object tree cannot be drawn as a json at once.)
    SchoolClass('FreshMen').register().modify_object('Students', School().get_property('Students')[:3])
    for s in SchoolClass('FreshMen').get_property('Students'):
        s.modify_object('SchoolClass', SchoolClass('FreshMen'))

    SchoolClass('Senior').register().modify_object('Students', School().get_property('Students')[3:])
    for s in SchoolClass('Senior').get_property('Students'):
        s.modify_object('SchoolClass', SchoolClass('Senior'))

    # now all items are stored in - can can be reconstructed from School() json
    print(School().to_json(all_properties_flag=True, indent=2))

    """
    {
      "Name": "School",
      "Class": "School",
      "Module": "__main__",
      "ClassRooms": [
        [     "Class" ,  "Module" ,  "Name" ],
        [ "ClassRoom" ,"__main__" ,"Room 1" ],
        [ "ClassRoom" ,"__main__" ,"Room 2" ],
        [ "ClassRoom" ,"__main__" ,  "Hall" ]
      ],
      "Schedule": [
        [  "Class" ,"ClassRoom" ,  "Module" ,  "Name" ,"SchoolClass" ,"Subject" ,   "Teacher" , "Time" ],
        [ "Lesson" ,   "Room 1" ,"__main__" ,"Lesson" ,   "FreshMen" ,   "Math" , "Mr. Logan" , "8:30" ],
        [ "Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,"Physics" , "Mr. Logan" ,"10:15" ],
        [ "Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,   "Math" , "Mr. Logan" ,"12:00" ],
        [ "Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,"History" ,"Mrs. Smith" , "8:30" ],
        [ "Lesson" ,     "Hall" ,"__main__" ,"Lesson" ,   "FreshMen" , "Sports" ,"Mrs. Smith" ,"10:15" ],
        [ "Lesson" ,   "Room 1" ,"__main__" ,"Lesson" ,   "FreshMen" ,"History" ,"Mrs. Smith" ,"12:00" ]
      ],
      "Students": [
        [   "Class" ,  "Module" , "Name" ,"SchoolClass" ],
        [ "Student" ,"__main__" ,  "Tom" ,   "FreshMen" ],
        [ "Student" ,"__main__" ,  "Ben" ,   "FreshMen" ],
        [ "Student" ,"__main__" ,"Luisa" ,   "FreshMen" ],
        [ "Student" ,"__main__" ,"Peter" ,     "Senior" ],
        [ "Student" ,"__main__" , "Paul" ,     "Senior" ],
        [ "Student" ,"__main__" , "Mary" ,     "Senior" ]
      ],
      "Teachers": [
        [   "Class" ,  "Module" ,      "Name" ],
        [ "Teacher" ,"__main__" , "Mr. Logan" ],
        [ "Teacher" ,"__main__" ,"Mrs. Smith" ]
      ]
    }
    """

    # for didactic purpose we set Schedule as a VisibleDataRange and all other lists as VisibleObjectList
    # (since `modify_object` would cast a VisibleObjectList to a TeacherList, StudentList or ClassRoomList
    #  we have to workaround here.)

    School()._teachers_ = VisibleObjectList(School().get_property('Teachers'))
    School()._students_ = VisibleObjectList(School().get_property('Students'))
    School()._class_rooms_ = VisibleObjectList(School().get_property('ClassRooms'))
    School()._schedule_ = VisibleDataRange(School().get_property('Schedule').to_serializable())

    # now we can not reconstructed from School() json as teachers, students and class rooms are only given by name
    print(School().to_json(all_properties_flag=True, indent=2))

    """
    {
      "Name": "School",
      "Class": "School",
      "Module": "__main__",
      "ClassRooms": [
        "Room 1",
        "Room 2",
        "Hall"
      ],
      "Schedule": [
        [ null , "Class" ,"ClassRoom" ,  "Module" ,  "Name" ,"SchoolClass" ,"Subject" ,   "Teacher" , "Time" ],
        [    0 ,"Lesson" ,   "Room 1" ,"__main__" ,"Lesson" ,   "FreshMen" ,   "Math" , "Mr. Logan" , "8:30" ],
        [    1 ,"Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,"Physics" , "Mr. Logan" ,"10:15" ],
        [    2 ,"Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,   "Math" , "Mr. Logan" ,"12:00" ],
        [    3 ,"Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,"History" ,"Mrs. Smith" , "8:30" ],
        [    4 ,"Lesson" ,     "Hall" ,"__main__" ,"Lesson" ,   "FreshMen" , "Sports" ,"Mrs. Smith" ,"10:15" ],
        [    5 ,"Lesson" ,   "Room 1" ,"__main__" ,"Lesson" ,   "FreshMen" ,"History" ,"Mrs. Smith" ,"12:00" ]
      ],
      "Students": [
        "Tom",
        "Ben",
        "Luisa",
        "Peter",
        "Paul",
        "Mary"
      ],
      "Teachers": [
        "Mr. Logan",
        "Mrs. Smith"
      ]
    }
    """

    # but we can extract all items we have so far and reconstruct from them
    for obj in VisibleObject.filter():
        print(VisibleObject(obj).to_json(all_properties_flag=False, indent=2))
        print()
        pass

    """
    {
      "Name": "School",
      "Class": "School",
      "Module": "__main__",
      "ClassRooms": [
        "Room 1",
        "Room 2",
        "Hall"
      ],
      "Schedule": [
        [ null , "Class" ,"ClassRoom" ,  "Module" ,  "Name" ,"SchoolClass" ,"Subject" ,   "Teacher" , "Time" ],
        [    0 ,"Lesson" ,   "Room 1" ,"__main__" ,"Lesson" ,   "FreshMen" ,   "Math" , "Mr. Logan" , "8:30" ],
        [    1 ,"Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,"Physics" , "Mr. Logan" ,"10:15" ],
        [    2 ,"Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,   "Math" , "Mr. Logan" ,"12:00" ],
        [    3 ,"Lesson" ,   "Room 2" ,"__main__" ,"Lesson" ,     "Senior" ,"History" ,"Mrs. Smith" , "8:30" ],
        [    4 ,"Lesson" ,     "Hall" ,"__main__" ,"Lesson" ,   "FreshMen" , "Sports" ,"Mrs. Smith" ,"10:15" ],
        [    5 ,"Lesson" ,   "Room 1" ,"__main__" ,"Lesson" ,   "FreshMen" ,"History" ,"Mrs. Smith" ,"12:00" ]
      ],
      "Students": [
        "Tom",
        "Ben",
        "Luisa",
        "Peter",
        "Paul",
        "Mary"
      ],
      "Teachers": [
        "Mr. Logan",
        "Mrs. Smith"
      ]
    }

    {
      "Name": "Mr. Logan",
      "Class": "Teacher",
      "Module": "__main__"
    }

    {
      "Name": "Mrs. Smith",
      "Class": "Teacher",
      "Module": "__main__"
    }

    {
      "Name": "Tom",
      "Class": "Student",
      "Module": "__main__",
      "SchoolClass": "FreshMen"
    }

    {
      "Name": "Ben",
      "Class": "Student",
      "Module": "__main__",
      "SchoolClass": "FreshMen"
    }

    {
      "Name": "Luisa",
      "Class": "Student",
      "Module": "__main__",
      "SchoolClass": "FreshMen"
    }

    {
      "Name": "Peter",
      "Class": "Student",
      "Module": "__main__",
      "SchoolClass": "Senior"
    }

    {
      "Name": "Paul",
      "Class": "Student",
      "Module": "__main__",
      "SchoolClass": "Senior"
    }

    {
      "Name": "Mary",
      "Class": "Student",
      "Module": "__main__",
      "SchoolClass": "Senior"
    }

    {
      "Name": "Room 1",
      "Class": "ClassRoom",
      "Module": "__main__"
    }

    {
      "Name": "Room 2",
      "Class": "ClassRoom",
      "Module": "__main__"
    }

    {
      "Name": "Hall",
      "Class": "ClassRoom",
      "Module": "__main__"
    }

    {
      "Name": "FreshMen",
      "Class": "SchoolClass",
      "Module": "__main__",
      "Students": [
        [   "Class" ,  "Module" , "Name" ,"SchoolClass" ],
        [ "Student" ,"__main__" ,  "Tom" ,   "FreshMen" ],
        [ "Student" ,"__main__" ,  "Ben" ,   "FreshMen" ],
        [ "Student" ,"__main__" ,"Luisa" ,   "FreshMen" ]
      ]
    }

    {
      "Name": "Senior",
      "Class": "SchoolClass",
      "Module": "__main__",
      "Students": [
        [   "Class" ,  "Module" , "Name" ,"SchoolClass" ],
        [ "Student" ,"__main__" ,"Peter" ,     "Senior" ],
        [ "Student" ,"__main__" , "Paul" ,     "Senior" ],
        [ "Student" ,"__main__" , "Mary" ,     "Senior" ]
      ]
    }
    """
