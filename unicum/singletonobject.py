# -*- coding: utf-8 -*-

# unicum
# ------
# Python library for simple object cache and factory.
# 
# Author:   sonntagsgesicht, based on a fork of Deutsche Postbank [pbrisk]
# Version:  0.3, copyright Wednesday, 18 September 2019
# Website:  https://github.com/sonntagsgesicht/unicum
# License:  Apache License 2.0 (see LICENSE file)


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
        return str(self)

    def __str__(self):
        return self.__class__.__name__
