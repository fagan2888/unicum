# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


class CachedObject(type):
    _cache = dict()
    _link = dict()

    def __call__(cls, name=''):
        name = 'Core' + cls.__name__  if name is '' else name
        if name not in CachedObject._cache:
            c = cls.__new__(cls, name)
            c.__init__(name)
            CachedObject._cache[name] = c
        return CachedObject._cache[name]

    @staticmethod
    def get(name, default=None):
        return CachedObject._cache[name] if name in CachedObject._cache else default

    @staticmethod
    def all(**kwargs):
        if kwargs:
            is_type = kwargs.pop('isinstance', None)
            l = list()
            for o in CachedObject._cache:
                obj = CachedObject._cache[o]
                if all([hasattr(obj, k) for k in kwargs]):
                    if all([getattr(obj, k) == kwargs[k] for k in kwargs]):
                        l.append(obj)
            if is_type:
                for o in l:
                    if isinstance(o, is_type):
                        l.remove(o)
            return l
        else:
            return CachedObject._cache

    @staticmethod
    def flush(name=None):
        if name is None:
            CachedObject._cache = dict()
        elif name in CachedObject._cache:
            CachedObject._cache.pop(name)

    @staticmethod
    def register(name, obj, attr):
        if name not in CachedObject._link:
            CachedObject._link[name] = set()
        if (obj, attr) not in CachedObject._link[name]:
            CachedObject._link[name].add((obj, attr))

    @staticmethod
    def update(name, value):
        CachedObject._cache[name] = value
        if name in CachedObject._link:
            for o, a in CachedObject._link[name]:
                if value is not getattr(o, a):
                    setattr(o, a, value)