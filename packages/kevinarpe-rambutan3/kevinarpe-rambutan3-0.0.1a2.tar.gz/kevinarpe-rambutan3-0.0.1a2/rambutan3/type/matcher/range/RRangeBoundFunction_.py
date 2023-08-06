from rambutan3 import RArgs
from rambutan3.type.matcher.range.RRangeBoundFunctionEnum_ import RRangeBoundFunctionEnum_

RRangeBoundFunction_ = None
class RRangeBoundFunction_:
    """
    This class exists only to be used by matchers.
    """

    def __init__(self, op_func_enum: RRangeBoundFunctionEnum_, value):
        RArgs.check_is_instance(op_func_enum, RRangeBoundFunctionEnum_, "op_func_enum")
        #: :type: RRangeBoundFunctionEnumData_
        self.__op_func_enum_data = op_func_enum.value
        self.__value = RArgs.check_not_none(value, "value")

    @property
    def op_func_enum_data(self):
        return self.__op_func_enum_data

    def __call__(self, value) -> bool:
        """ This is the function operator: () """
        RArgs.check_not_none(value, "value")
        x = self.__op_func_enum_data.op_func(value, self.__value)
        return x

    def __contains__(self, other) -> bool:
        """ This is the membership operator: in """
        RArgs.check_is_instance(other, RRangeBoundFunction_, "other")
        if (self.__op_func_enum_data.op_func is other.__op_func_enum_data.op_func) \
                or (self.__same_side(other) and self.__includes(other)):
            x = self.__op_func_enum_data.op_func(other.__value, self.__value)
            return x
        else:
            return False

    def __same_side(self, other: RRangeBoundFunction_) -> bool:
        x = self.__op_func_enum_data.is_greater == other.__op_func_enum_data.is_greater
        return x

    def __includes(self, other: RRangeBoundFunction_) -> bool:
        # >= includes >, but > does not include >=, and vice versa
        x = self.__op_func_enum_data.is_inclusive or not other.__op_func_enum_data.is_inclusive
        return x

    def __eq__(self, other: RRangeBoundFunction_) -> bool:
        if not isinstance(other, RRangeBoundFunction_):
            return False
        x = (self.__op_func_enum_data == other.__op_func_enum_data and self.__value == other.__value)
        return x

    def __hash__(self) -> int:
        x = hash((self.__op_func_enum_data, self.__value))
        return x

    def __str__(self):
        # Example: "x >= 3"
        x = "x {} {}".format(self.__op_func_enum_data.op, self.__value)
        return x
