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
from ranger import dict_from_range, range_from_dict

_order = 'Name', 'Class', 'Module'


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
        # return self.__class__.__name__ + '(' + self._name + ')'
        return str(self._name)

    def get_property(self, property_name, property_item_name=None):
        if not self.__class__._is_visible(property_name):
            property_name = self.__class__._to_visible(property_name)
        if property_item_name is None:
            return getattr(self, property_name)
        raise AttributeError

    def to_serializable(self, level=0, all_properties_flag=False):
        if level is 0:
            return PersistentObject.to_serializable(self, all_properties_flag=all_properties_flag)
        else:
            return FactoryObject.to_serializable(self, all_properties_flag)

    def to_range(self, all_properties_flag=False):
        s = self.to_serializable(0, all_properties_flag)
        r = range_from_dict(s, _order)
        return r

    @classmethod
    def from_serializable(cls, item, register_flag=False):
        if isinstance(item, list):
            obj = [o for o in VisibleAttributeList.from_serializable(item)]
        elif isinstance(item, dict):
            obj = PersistentObject.from_serializable(item)
            if register_flag:
                obj.register()
            obj.update_link()
        else:
            obj = FactoryObject.from_serializable(str(item))
        return obj

    @classmethod
    def from_range(cls, range_list, register_flag=True):
        """ core class method to create visible objects from a range (nested list) """
        s = dict_from_range(range_list)
        obj = cls.from_serializable(s, register_flag)
        return obj

    @classmethod
    def create(cls, name=None, register_flag=False, **kwargs):
        key_name = cls._from_visible(cls.STARTS_WITH + 'name' + cls.ENDS_WITH)
        if name is None:
            name = kwargs[key_name] if key_name in kwargs else cls.__name__
            kwargs['name'] = name
        obj = cls(str(name))
        obj.modify_object(kwargs)
        if register_flag:
            obj.register()
        return obj


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
                 none_alias=(None, ' ', '', 'None')):
        super(VisibleDataRange, self).__init__(iterable, value_types, none_alias)
