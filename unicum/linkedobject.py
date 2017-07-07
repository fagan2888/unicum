# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


import inspect


class LinkedObject(object):
    """ links from linked_obj to (obj, attribute) with obj.attribute = linked_obj """
    __link = dict()

    @property
    def _name(self):
        return str(self)

    @classmethod
    def _get_links(cls):
        mro = inspect.getmro(cls)
        for m in mro:
            attr = '_' + m.__name__ + '__link'
            if hasattr(cls, attr):
                return getattr(cls, attr)
        raise TypeError

    def __repr__(self):
        return self.__class__.__name__ + '.' + str(self) + '(' + str(id(self)) + ')'

    def __str__(self):
        return str(self.__class__.__name__)

    def __setattr__(self, item, value):
        if hasattr(self, item):
            current = getattr(self, item)
            if isinstance(current, LinkedObject):
                current.remove_link(self, item)
        super(LinkedObject, self).__setattr__(item, value)
        if isinstance(value, LinkedObject):
            value.register_link(self, item)

    def register_link(self, obj, attr=None):
        """
        creates link from obj.attr to self
        :param obj: object to register link to
        :param attr: attribute name to register link to
        """
        name = self._name
        l = self.__class__._get_links()
        if name not in l:
            l[name] = set()
        v = (obj, attr)
        if v not in l:
            l[name].add(v)
        return self

    def remove_link(self, obj, attr=None):
        """
        removes link from obj.attr
        """
        name = self._name
        l = self.__class__._get_links()
        v = (None, obj) if attr is None else (obj, attr)
        if v in l[name]:
            l[name].remove(v)
        if not l[name]:
            l.pop(name)
        return self

    def update_link(self):
        """
        redirects all links to self (the new linked object)
        """
        name = self._name
        l = self.__class__._get_links()
        to_be_changed = list()
        if name in l:
            for o, a in l[name]:
                if self is not getattr(o, a, None):
                    to_be_changed.append((o,a))
        for o, a in to_be_changed:
            setattr(o, a, self)

        return self
