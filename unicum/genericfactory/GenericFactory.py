"""
module containing GenericFactory class
"""


class GenericFactory(object):
    """
    implementation of generic __factory used for object creation
    """

    # instance = None
    #
    # @staticmethod
    # def get_instance():
    #     if GenericFactory.instance is None:
    #         GenericFactory.instance = GenericFactory()
    #
    #     return GenericFactory.instance

    def register(self, object_id, creator):
        """
        register object creator for given id

        :param object object_id : object_id. It must be immutable.
        :param object creator : object creator
        :return bool :
        """

        res = False
        if object_id not in self.__factory_dict:
            self.__factory_dict[object_id] = creator
            res = True
            if not self.__default_value:
                self.__default_value = creator

        return res

    def create_object(self, object_id=None, *create_params):
        """
        create object based on the given id and given parameters

        :param object object_id : id of constructed object (e.g. class name)
        :param iterable create_params : parameters required for creation (if any)
        :return object :
        """

        if not object_id:
            object_id = self.__default_value
        res = self.__internal_create_object(object_id)
        if len(create_params) > 0:
            res = res(*create_params)

        return res

    def __init__(self):
        """
        initializer
        """

        #: dictionary to keep track of the objects
        self.__factory_dict = dict()
        self.__default_value = None

    def keys(self):
        """
        returns keys in the __factory

        @return list :
        """

        return self.__factory_dict.keys()

    def __internal_create_object(self, object_id):
        """
        returns object creator functor based on object_id

        :param object object_id : immutable object id
        :return object :
        """

        return self.__factory_dict[object_id]
