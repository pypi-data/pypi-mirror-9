from enum import Enum


class REnum(Enum):

    def __init__(self, *args, **kwargs):
        super().__init__()
        self.__full_name = "{}.{}".format(type(self).__name__, self.name)

    @property
    def full_name(self):
        return self.__full_name
