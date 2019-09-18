# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


import inspect
from six import with_metaclass

class FactoryType(type):

    def __call__(cls, *args, **kwargs):
        name = str(args[0]) if args else cls.__name__
        name = kwargs['name'] if 'name' in kwargs else name
        instance = cls.get(name)
        if instance is None:
            instance = cls.__new__(cls, *args, **kwargs)
            instance.__init__(*args, **kwargs)
        return instance

    @classmethod
    def get(cls, key, default=None):
        return default


class FactoryObject(with_metaclass(FactoryType, object)):  # 2to3 migration 20190915
    """ Objects identified by name """

    __factory = dict()

    def __init__(self, *args, **kwargs):
        super(FactoryObject, self).__init__()

    @classmethod
    def _get_factory(cls):
        mro = inspect.getmro(cls)
        for m in mro:
            attr = '_' + m.__name__ + '__factory'
            if hasattr(cls, attr):
                return getattr(cls, attr)
        raise TypeError

    def __repr__(self):
        return str(self)

    def __str__(self):
        return self.__class__.__name__

    def register(self, *names):
        factory = self.__class__._get_factory()
        if not names:
            names = (repr(self),)
        for name in names:
            factory[str(name)] = self
        return self

    def remove(self):
        factory = self.__class__._get_factory()
        for k, v in list(factory.items()):
            if v == self:
                factory.pop(k)
        return self

    def to_serializable(self, level=0, all_properties_flag=False, recursive=True):
        return repr(self)

    @classmethod
    def from_serializable(cls, item):
        return cls(item)

    @classmethod
    def filter(cls, filter_func=None):
        if filter_func is None:
            return list(cls.keys())

        factory = cls._get_factory()
        return sorted([k for k, v in list(factory.items()) if filter_func(v)])

    @classmethod
    def get(cls, key, default=None):
        factory = cls._get_factory()
        return factory.get(key, default)

    @classmethod
    def keys(cls):
        factory = cls._get_factory()
        return list(factory.keys())

    @classmethod
    def values(cls):
        factory = cls._get_factory()
        return list(factory.values())

    @classmethod
    def items(cls):
        factory = cls._get_factory()
        return list(factory.items())


class ObjectList(list):

    def __init__(self, iterable=None, object_type=FactoryObject):
        if not issubclass(object_type, FactoryObject):
            raise TypeError('Required object type of ObjectList items must be subtype of %s ' % FactoryObject.__name__)
        self._object_type = object_type
        if iterable is None:
            super(ObjectList, self).__init__()
        else:
            i = list()
            for x in iterable:
                if type(x) is not str:
                    self.__validate(x)
                else:
                    x = self._object_type(x)
                i.append(x)
            iterable = i
            for x in iterable:
                self.__validate(x)
            super(ObjectList, self).__init__(iterable)

    def __repr__(self):
        return self.__class__.__name__ + '(' + str(self) + ', %s)' % self._object_type.__name__

    def __str__(self):
        return '[' +  ', '.join(repr(x) for x in self) + ']'

    def __validate(self, x):
        if not isinstance(x, self._object_type):
            raise TypeError('All items in this ObjectList must be of subtype of %s ' %self._object_type.__name__)

    def __cast(self, x):
        return x if isinstance(x, self._object_type) else self._object_type(x)

    def __iter__(self):
        return super(ObjectList, self).__iter__()

    def __setitem__(self, key, value):
        value = self.__cast(value)
        self.__validate(value)
        super(ObjectList, self).__setitem__(key, value)

    def __contains__(self, item):
        if isinstance(item, self._object_type):
            return super(ObjectList, self).__contains__(item)
        return item in [str(f) for f in self]

    def index(self, item, start=None, stop=None):
        if start is None or stop is None:
            if isinstance(item, self._object_type):
                return super(ObjectList, self).index(item)
            elif type(item) is str:
                return [str(f) for f in self].index(item)
        return [f.to_serializable() for f in self].index(item, start, stop)

    def __getitem__(self, item):
        if isinstance(item, self._object_type):
            return [o for o in self if o == item][0]
        elif type(item) is str:
            return [o for o in self if str(o) == item][0]
        return super(ObjectList, self).__getitem__(item)

    def get(self, item, default=None):
        return self[item] if item in self else default

    def __add__(self, other):
        other = [self.__cast(value) for value in other]
        for value in other:
            self.__validate(value)
        return ObjectList(super(ObjectList, self).__add__(other), self._object_type)

    def __iadd__(self, other):
        other = [self.__cast(value) for value in other]
        for value in other:
            self.__validate(value)
        return self.__class__(super(ObjectList, self).__iadd__(other), self._object_type)

    def __setslice__(self, i, j, iterable):
        iterable = [self.__cast(value) for value in iterable]
        for value in iterable:
            self.__validate(value)
        super(ObjectList, self).__setslice__(i, j, iterable)

    def append(self, value):
        value = self.__cast(value)
        self.__validate(value)
        super(ObjectList, self).append(value)

    def insert(self, index, value):
        value = self.__cast(value)
        self.__validate(value)
        super(ObjectList, self).insert(index, value)

    def extend(self, iterable):
        iterable = [self.__cast(value) for value in iterable]
        for value in iterable:
            self.__validate(value)
        super(ObjectList, self).extend(iterable)

    def to_serializable(self, level=0, all_properties_flag=False, recursive=True):
        if recursive:
            return [x.to_serializable(level + 1, all_properties_flag) for x in self]
        else:
            return list(self)

    @classmethod
    def from_serializable(cls, item):
        return cls(item)

    def __reduce__(self):
        return self.__class__, (list(self), self._object_type)
