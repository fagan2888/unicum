"""
  module containing StringSerialization mixin
"""


class StringSerialization(object):
    """
     implementation of mixin for/to string serialization

    :version:
    :author:
    """

    # definition for pylint (real FactoryObject should be defined in subclass)
    Factory = None

    def to_string(self):
        """
        returns __name__ attribute of the instance used  used by persistence framework
        for object persistence

        @return string :
        @author
        """
        return type(self).__name__

    @classmethod
    def from_string(cls, name):
        """
        returns day count convention instance based on the name

        @param string name : object_id used for construction from cls.FactoryObject \
        e.g. Act360, Act365, D30360
        @return object : e.g businessdate.DayCount
        @author
        """
        return cls.Factory.create_object(name)

    def __repr__(self):
        return self.to_string()

    def __str__(self):
        return type(super(StringSerialization,self)).__class__.__name__ + '(' + self.to_string() + ')'
