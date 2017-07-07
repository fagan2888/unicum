# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


import datetime
import getpass
import json

from decode_json import decode_dict as _decode_dict


class PersistentObject(object):
    STARTS_WITH = '_'
    ENDS_WITH = '_'
    JSON_INDENT = 2

    @property
    def is_modified(self):
        return len(self._modified_members) > 0

    @property
    def _class(self):
        return str(self.__class__.__name__)

    @property
    def _module(self):
        return str(self.__module__)

    def __init__(self, *args, **kwargs):
        super(PersistentObject, self).__init__()
        setattr(self, self.__class__.STARTS_WITH + 'class' + self.__class__.ENDS_WITH, self._class)
        setattr(self, self.__class__.STARTS_WITH + 'module' + self.__class__.ENDS_WITH, self._module)
        self._ts_create = datetime.datetime.now()
        self._user_create = getpass.getuser() if hasattr(getpass, 'getuser') else 'NoUser'
        self._ts_update = self._ts_create
        self._user_update = self._user_create
        self._modified_members = []
        self._version = 0

    def __repr__(self):
        return self.__class__.__name__ + '.' + str(self) + '(' + str(id(self)) + ')'

    def __str__(self):
        return str(self.__class__.__name__)

    @classmethod
    def _is_visible(cls, property_name):
        """ private method to check visible object property to be visible """
        if isinstance(property_name, list):
            return [cls._is_visible(p) for p in property_name]
        if property_name.startswith('__') and property_name.endswith('__'):
            return False
        return property_name.startswith(cls.STARTS_WITH) and property_name.endswith(cls.ENDS_WITH)

    @classmethod
    def _from_visible(cls, property_name):
        if isinstance(property_name, list):
            return [cls._from_visible(p) for p in property_name]
        if cls._is_visible(property_name):
            property_name = property_name[len(cls.STARTS_WITH):-len(cls.ENDS_WITH)]
            m_list = str(property_name).split('_')
            n = [l.capitalize() for l in m_list if l]
            return ''.join(n)
        return property_name

    @classmethod
    def _to_visible(cls, property_name):
        if isinstance(property_name, list):
            return [cls._to_visible(p) for p in property_name]
        if cls._is_visible(property_name):
            return property_name
        n = [property_name[0].lower()]
        for l in property_name[1:]:
            n.append('_' + l.lower()) if l.isupper() else n.append(l)
        return cls.STARTS_WITH + ''.join(n) + cls.ENDS_WITH

    @classmethod
    def _from_class(cls, class_name, module_name=None, *args, **kwargs):
        """ class method to create object of a given class """

        if module_name:
            # module = globals()[module_name]
            module = __import__(module_name)
            class_ = getattr(module, class_name)
        else:
            class_ = globals()[class_name]

        if not issubclass(class_, PersistentObject):
            t = class_.__name__, PersistentObject.__name__
            raise TypeError, 'Requested object type %s must be subtype of %s ' % t

        # workaround to mimic FactoryType to work well with FactoryObject.
        name = str(args[0]) if args else cls.__name__
        name = kwargs['name'] if 'name' in kwargs else name
        if hasattr(cls, '_get'):
            instance = cls._get(name)
            if instance:
                return instance

        instance = class_.__new__(class_, *args, **kwargs)
        instance.__init__(*args, **kwargs)
        return instance

    @classmethod
    def from_serializable(cls, object_dict):
        """ core class method to create visible objects from a dictionary """

        key_class = cls._from_visible(cls.STARTS_WITH + 'class' + cls.ENDS_WITH)
        key_module = cls._from_visible(cls.STARTS_WITH + 'module' + cls.ENDS_WITH)

        obj_class = object_dict.pop(key_class)
        obj_module = object_dict.pop(key_module) if key_module in object_dict else None

        obj = cls._from_class(obj_class, obj_module)
        obj.modify_object(object_dict)
        return obj

    @classmethod
    def from_json(cls, json_str):
        obj_dict = json.loads(json_str, object_hook=_decode_dict)
        if isinstance(obj_dict, dict):
            return cls.from_serializable(obj_dict)
        else:
            return [cls.from_serializable(d) for d in obj_dict]

    def to_serializable(self, level=0, all_properties=False):
        d = dict()
        for a in [a for a in dir(self) if self.__class__._is_visible(a)]:
            if a in self._modified_members or self._from_visible(a) in ['Name', 'Class', 'Module'] or all_properties:
                v = getattr(self, a)
                v = v if not hasattr(v, 'to_serializable') else v.to_serializable(level + 1)
                v = v if isinstance(v, (float, int, list, type(None))) else str(v)
                d[self.__class__._from_visible(a)] = v
        return d

    def to_json(self, indent=2, all_properties=False):
        obj_dict = self.to_serializable(all_properties=all_properties)
        # todo better pretty print for DataRange and AttributeList (nested list)
        return json.dumps(obj_dict, indent=indent, sort_keys=True)

    def modify_object(self, property_name, property_value=None):
        """
        api visible method for modifying visible object properties

        :param property_name: property name
        :type property_name: string, list or dict
        :param property_value: property value, must be `None` if property_name is of type `dict`
        :type property_value: various or None
        :return: modified object
        :rtype: unicum.lfojbect.VisibleObject
        """
        if type(property_name) is dict:
            property_value = property_name.values()
            property_name = property_name.keys()

        if isinstance(property_name, str):
            property_name, property_value = [property_name], [property_value]
        assert len(property_name) == len(property_value)

        # convert names into visible
        property_name = self.__class__._to_visible(property_name)

        # loop over properties to set
        for n, v in zip(property_name, property_value):
            self._modify_property(n, v)

        # rebuild object in order to maintain consistency
        self._rebuild_object()
        return self

    def _modify_property(self, property_name, property_value):
        # avoid circles
        if property_value is self:
            raise ValueError, 'Attributes must not be recursively. Not mapping self to %s.' % property_name

        # handle not admissible property_name type
        if not isinstance(property_name, str):
            s = str(property_name), type(property_name), self.__class__.__name__
            msg = 'can not handle %s of type %s as a property in object of type %s' % s
            print(msg)
            # raise TypeError, msg
            return

        # handle not admissible property_name
        if not hasattr(self, property_name) or not self.__class__._is_visible(property_name):
            if property_name:
                s = property_name, self.__class__.__name__, str(self)
                msg = 'property %s in object of type %s not found in %s' % s
                print(msg)
                # raise ValueError, msg
                return

        # check type of property_value
        current_property_value = getattr(self, property_name)
        if not isinstance(property_value, type(current_property_value)):
            property_value = current_property_value.__class__(property_value)

        # finally set new property value
        setattr(self, property_name, property_value)

        # update timestamps and version
        self._ts_update = datetime.datetime.now()
        self._user_update = getpass.getuser() if hasattr(getpass, 'getuser') else 'NoUser'
        self._version += 1
        self._modified_members.append(property_name)

    def _rebuild_object(self):
        """ method to initiate a visible object rebuild """
        pass


# container class of list of objects
class AttributeList(list):
    """ object list class """

    def __reduce__(self):
        return self.__class__, (list(self), self._object_type, self._value_types)

    def __init__(self, iterable=None, object_type=PersistentObject, value_types=(float, int, str, type(None))):
        if not issubclass(object_type, PersistentObject):
            raise TypeError, \
                'Required object type of AttributeList items must be subtype of %s ' % PersistentObject.__name__
        self._object_type = object_type
        self._value_types = value_types
        if iterable is None or len(iterable) is 0:  # iterable is None
            super(AttributeList, self).__init__()
        else:
            # must be or build object_type
            # list of lists -> list of dicts
            if all([type(x) is list for x in iterable]):  # iterable is nested list of object properties
                keys = tuple(iterable.pop(0))  # extract headline of property names
                if not len(keys) == len(set(keys)):
                    raise ValueError, 'Properties in AttributeList must be unique'
                iterable = [self._object_from_serializable(x, keys) for x in iterable]
            elif all([type(x) is dict for x in iterable]):  # iterable is list of dict of object properties
                iterable = [self._object_from_serializable(x) for x in iterable]
            # validate objects
            for x in iterable:
                self._validate(x)
            super(AttributeList, self).__init__(iterable)

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self) + ', %s)' % self._object_type.__name__

    def __str__(self):
        return '[' + ', '.join(repr(x) for x in self) + ']'

    def _object_from_serializable(self, x, keys=None):
        if isinstance(x, list):
            x = dict(zip(keys, x))
        if isinstance(x, dict):
            x = self._object_type.from_serializable(x)
        return x if isinstance(x, self._object_type) else self._object_type(x)

    def _validate(self, x):
        if not isinstance(x, self._object_type):
            raise TypeError, 'All items in this AttributeList must have subtype of %s.' % self._object_type.__name__
        for k, v in x.to_serializable().items():
            if not isinstance(v, self._value_types):
                s = ', '.join([str(t) for t in self._value_types])
                t = type(v)
                raise TypeError, \
                    'All properties of item in this AttributeList must have type ' \
                    'of either one of %s but not %s as seen for property %s' % (s, t, k)

    def __iter__(self):
        return super(AttributeList, self).__iter__()

    def __setitem__(self, key, value):
        value = self._object_from_serializable(value)
        self._validate(value)
        super(AttributeList, self).__setitem__(key, value)

    def __add__(self, iterable):
        iterable = [self._object_from_serializable(value) for value in iterable]
        for value in iterable:
            self._validate(value)
        return self.__class__(super(AttributeList, self).__add__(iterable), self._object_type)

    def __iadd__(self, iterable):
        iterable = [self._object_from_serializable(value) for value in iterable]
        for value in iterable:
            self._validate(value)
        return self.__class__(super(AttributeList, self).__iadd__(iterable), self._object_type)

    def __setslice__(self, i, j, iterable):
        iterable = [self._object_from_serializable(value) for value in iterable]
        for value in iterable:
            self._validate(value)
        super(AttributeList, self).__setslice__(i, j, iterable)

    @classmethod
    def from_serializable(cls, item):
        return cls(item)

    def append(self, value):
        value = self._object_from_serializable(value)
        self._validate(value)
        super(AttributeList, self).append(value)

    def index(self, value, start=None, stop=None):
        value = self._object_from_serializable(value)
        self._validate(value)
        return super(AttributeList, self).index(value, start, stop)

    def insert(self, index, value):
        value = self._object_from_serializable(value)
        self._validate(value)
        super(AttributeList, self).insert(index, value)

    def extend(self, iterable):
        iterable = [self._object_from_serializable(value) for value in iterable]
        for value in iterable:
            self._validate(value)
        super(AttributeList, self).extend(iterable)

    def to_serializable(self, level=0):
        if not self:
            return [['Name', 'Class', 'Module']]
        # list of objects -> list of dicts
        d = [x.to_serializable() for x in self]
        keys = sorted(self.keys())
        ret = [keys]
        for o in d:
            l = list()
            for k in keys:
                v = o.get(k, None)
                v = v if not hasattr(v, 'to_serializable') else v.to_serializable(level + 1)
                v = v if isinstance(v, self._value_types) else str(v)
                # v = v if isinstance(v, (float, int, type(None))) else str(v)
                l.append(v)
            ret.append(l)
        return ret

    def keys(self):
        return sorted(set().union(*[x.to_serializable().keys() for x in self]))

    def values(self):
        keys = self.keys()
        dicts = [x.to_serializable() for x in self]
        return [[o.get(k) for k in keys] for o in dicts]

    def items(self):
        return zip(self.keys(), self.items())
