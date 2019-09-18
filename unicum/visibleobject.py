# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


import json

from .factoryobject import FactoryObject, ObjectList
from .linkedobject import LinkedObject
from .persistentobject import PersistentObject, AttributeList, _order
from .datarange import DataRange
from .ranger import dict_from_range, range_from_dict
from .encode_json import UnicumJSONEncoder
from .decode_json import decode_dict as _decode_dict


class VisibleObject(FactoryObject, LinkedObject, PersistentObject):
    __factory = dict()
    __link = dict()

    def __init__(self, *args, **kwargs):
        super(VisibleObject, self).__init__(*args, **kwargs)
        name = str(args[0]) if args else self.__class__.__name__
        name = kwargs['name'] if 'name' in kwargs else name
        self._name_ = name

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self._name_

    def get_property(self, property_name, property_item_name=None):
        if not self.__class__._is_visible(property_name):
            property_name = self.__class__._to_visible(property_name)
        if property_item_name is None:
            return getattr(self, property_name)
        raise AttributeError

    def to_serializable(self, level=0, all_properties_flag=False, recursive=True):
        if level is 0:
            return PersistentObject.to_serializable(self, all_properties_flag=all_properties_flag, recursive=recursive)
        else:
            return FactoryObject.to_serializable(self, all_properties_flag, recursive=recursive)

    def to_json(self, all_properties_flag=False, property_order=_order, **kwargs):
        kwargs['cls'] = kwargs.pop('cls', UnicumJSONEncoder)
        if issubclass(kwargs['cls'], UnicumJSONEncoder):
            kwargs['key_order'] = property_order
            kwargs['all_properties_flag'] = all_properties_flag
            obj = self
        else:
            obj = self.to_serializable(all_properties_flag=all_properties_flag)
        return json.dumps(obj, **kwargs)

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
    def from_json(cls, json_str):
        obj_dict = json.loads(json_str, object_hook=_decode_dict)
        if isinstance(obj_dict, dict):
            return cls.from_serializable(obj_dict)
        else:
            return [cls.from_serializable(d) for d in obj_dict]

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
            #     name = kwargs[key_name] if key_name in kwargs else cls.__name__
            #     kwargs['name'] = name
            obj = cls()
        else:
            obj = cls(str(name))
        obj.modify_object(kwargs)
        if register_flag:
            obj.register()
        return obj


class VisibleList(list):

    def register(self):
        for x in self:
            x.register()
        return self


class VisibleObjectList(ObjectList, VisibleList):
    def __init__(self, iterable=None, object_type=VisibleObject):
        super(VisibleObjectList, self).__init__(iterable, object_type)


class VisibleAttributeList(AttributeList, VisibleList):
    def __init__(self, iterable=None, object_type=VisibleObject,
                 value_types=(float, int, str, type(None), VisibleObject)):
        super(VisibleAttributeList, self).__init__(iterable, object_type, value_types)


class VisibleDataRange(DataRange):
    def __init__(self, iterable=None,
                 value_types=(float, int, str, type(None), VisibleObject),
                 none_alias=(None, ' ', '', 'None')):
        super(VisibleDataRange, self).__init__(iterable, value_types, none_alias)
