# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


import functools

'''
    cache keys are not case sensitive, eg actACT for ActAct
    cache returns proper capitalisation, eg ActAct for actact
    caches named objects by obj.name
    caches unnamed objects by obj.__class__.__name__

    class actact(daycount): pass

    daycount()==cache('daycount')
    daycount()==actact()
    daycount('30/360')==Thirty360()

    pricer()==

'''


def _to_string(cls):
    return str(cls.__name__)


class _CaseInsensitiveDict(dict):
    """ dict with case insensitive keys """

    def __setitem__(self, k, d):
        """ handle key case insensitive """
        return super(_CaseInsensitiveDict, self).__setitem__(k.upper(), d)

    def __contains__(self, k):
        """ handle key case insensitive """
        return super(_CaseInsensitiveDict, self).__contains__(k.upper())

    def __getitem__(self, k):
        """ handle key case insensitive """
        try:
            return super(_CaseInsensitiveDict, self). __getitem__(k.upper())
        except:
            return None

    def __delitem__(self, k):
        """ handle key case insensitive """
        return super(_CaseInsensitiveDict, self).__delitem__(k.upper())

    def pop(self, k, d=None):
        """ handle key case insensitive """
        return super(_CaseInsensitiveDict, self).pop(k.upper(), d)


class Factory(object):
    """ FactoryObject class to manage cache of named objects.
        Behaves like a dict. Is callable to factor items. """

    def __init__(self, cache=None, required_type=None, default_key=None, key_func=(lambda x: x.to_serializable())):
        self.cache = cache
        if not self.cache:
            self.cache = _CaseInsensitiveDict()
        if required_type and not isinstance(required_type, type):
            # type might be wrapper used for decorator
            required_type = required_type.__closure__[0].cell_contents
        self.type = required_type
        self.default_key = default_key
        self.key_func = key_func

    def __call__(self, key=None):
        if not key:
            key = self.default_key
        if not key:
            raise KeyError, '__factory default key not set.'
        value = self.cache[key]
        if self.type:
            assert isinstance(value, self.type)
        return value

    def __str__(self):
        if self.type:
            d = [k for k in self.cache if isinstance(self.cache[k],self.type)]
            l = max([len(k) for k in d])
            return '\n'.join([self.__class__.__name__ + '.' + self.type.__name__ + '.' \
                    + k.ljust(l)+':'+repr(self.cache[k]) for k in d])

        l = max([len(k) for k in self.cache])
        return '\n'.join([self.__class__.__name__ + '.' + k.ljust(l,)+':'+repr(self.cache[k]) for k in self.cache])

    def __setitem__(self, k, d):
        if not hasattr(d,'to_serializable'):
            setattr(d.__class__, 'to_serializable', classmethod(_to_string))
        return self.cache.__setitem__(k, d)

    def __contains__(self, k):
        return self.cache.__contains__(k)

    def __getitem__(self, k):
        return self.cache.__getitem__(k)

    def __delitem__(self, k):
        return self.cache.__delitem__(k)

    def pop(self, k, d=None):
        return self.cache.pop(k, d)


class DecoratorFactory(Factory):
    """ FactoryObject class to manage cache of named objects.
        Behaves like a dict. Is callable to factor items.
        Provides easy to use as decorators. """

    def by_auto(self, obj):
        @functools.wraps(obj)
        def factory_wrapper(*args, **kwargs):

            # retrieve key entry
            if not args:
                if self.default_key:
                    # default to self.default_key as key
                    key = self.default_key
                else:
                    # default to obj.__name__ as key
                    key = obj.__name__
            elif len(args) == 1:
                # in case of a single arg (name), take this entry as key
                key = str(args[0])
            else:
                # else store all call args
                key = str(args)

            # retrieve value entry
            if key in self.cache:
                # grab item identified by first argument
                value = self.cache[key]
            else:
                # if no item can be identified create a new one
                value = obj(args)
                # add the identified item to keys given by arguments
                self.cache[key] = value
                if obj.__name__ not in self:
                    # if no default is set do it now
                    self.cache[obj.__name__] = value

            if self.type:
                assert isinstance(value, self.type)
            return value

        return factory_wrapper

    def by_args(self, obj):
        @functools.wraps(obj)
        def factory_wrapper_by_args(*args):
            # retrieve item key
            key = str(args)
            # retrieve item
            if key not in self.cache:
                self.cache[key] = obj(args)
            value = self.cache[key]
            if self.type:
                assert isinstance(value, self.type)
            return value

        return factory_wrapper_by_args

    def by_key(self, obj):
        @functools.wraps(obj)
        def factory_wrapper_by_key(*args):
            # if no args given return obj but not cached
            if not args:
                return obj(args)
            # retrieve item key
            key = str(args[0])
            # retrieve item
            if key not in self.cache:
                self.cache[key] = obj(args)
            value = self.cache[key]
            if self.type:
                assert isinstance(value, self.type)
            return value
        return factory_wrapper_by_key

    def by_class_name(self, obj):
        @functools.wraps(obj)
        def factory_wrapper_by_class_name(*args):
            # retrieve item key
            key = obj.__name__
            # retrieve item
            if key not in self.cache:
                self.cache[key] = obj(*args)
            value = self.cache[key]
            if self.type:
                assert isinstance(value, self.type)
            return value
        return factory_wrapper_by_class_name

