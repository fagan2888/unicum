# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


from factoryobject import FactoryObject, ObjectList
from linkedobject import LinkedObject
from persistentobject import PersistentObject, AttributeList
from datarange import DataRange


class VisibleObject(FactoryObject, LinkedObject, PersistentObject):
    def __init__(self, *args, **kwargs):
        super(VisibleObject, self).__init__(*args, **kwargs)
        name = str(args[0]) if args else self.__class__.__name__
        name = kwargs['name'] if 'name' in kwargs else name
        self._name_ = name

    @property
    def _name(self):
        return self._name_

    def __repr__(self):
        return str(self) + '(' + str(id(self)) + ')'

    def __str__(self):
        return self.__class__.__name__ + '(' + self._name + ')'

    def to_serializable(self, level=0, all_properties=False):
        if level is 0:
            return PersistentObject.to_serializable(self, all_properties=all_properties)
        else:
            return FactoryObject.to_serializable(self)

    @classmethod
    def from_serializable(cls, item):
        if isinstance(item, list):
            return [o for o in VisibleAttributeList.from_serializable(item)]
        elif isinstance(item, dict):
            return PersistentObject.from_serializable(item)
        else:
            return FactoryObject.from_serializable(str(item))


class VisibleObjectList(ObjectList):
    def __init__(self, iterable=None, object_type=VisibleObject):
        super(VisibleObjectList, self).__init__(iterable, object_type)


class VisibleAttributeList(AttributeList):
    def __init__(self, iterable=None, object_type=VisibleObject,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(VisibleAttributeList, self).__init__(iterable, object_type, value_types)


class VisibleDataRange(DataRange):
    def __init__(self, iterable=None,
                 value_types=(float, int, str, type(None), VisibleObject),
                 none_alias=(None, ' ', '', None)):
        super(VisibleDataRange, self).__init__(iterable, value_types, none_alias)
