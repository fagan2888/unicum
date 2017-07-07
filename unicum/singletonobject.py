# -*- coding: utf-8 -*-

#  unicum
#  ------------
#  Simple object cache and __factory.
#
#  Author:  pbrisk <pbrisk_at_github@icloud.com>
#  Copyright: 2016, 2017 Deutsche Postbank AG
#  Website: https://github.com/pbrisk/unicum
#  License: APACHE Version 2 License (see LICENSE file)


class SingletonObject(object):
    """Use to create a singleton"""

    def __new__(cls):
        self = "__self__"
        if not hasattr(cls, self):
            instance = object.__new__(cls)
            instance.__init__()
            setattr(cls, self, instance)
        return getattr(cls, self)

    def __repr__(self):
        return str(self) + '(' + str(id(self)) + ')'

    def __str__(self):
        return self.__class__.__name__