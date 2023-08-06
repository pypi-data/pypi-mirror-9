import random
from rambutan3 import RArgs
from rambutan3.type.matcher.range.RRangeBound_ import RRangeBound_
from rambutan3.type.matcher.range.RRangeBoundFunction_ import RRangeBoundFunction_
from rambutan3.type.matcher.range.RRangeBoundFunctionEnum_ import RRangeBoundFunctionEnum_
from rambutan3.type.matcher.range.RRangeBoundFunctionEnumData_ import RRangeBoundFunctionEnumData_


RRange_ = None
class RRange_:
    """
    This class exists only to be used by matchers.
    """

    __PRIVATE_CTOR_KEY = random.randint(0, 256)

    #: :type: dict of (str, _RRangeBoundFunctionEnumData)
    __BOUND_OP_TO_DATA_DICT = {x.value.op: x for x in RRangeBoundFunctionEnum_.__members__.values()}

    @classmethod
    def create(cls, bound_op1: str, value1, opt_bound_op2: str, opt_value2) -> RRange_:
        if not opt_bound_op2:
            x = cls.for_one_bound(bound_op1, value1)
        else:
            x = cls.for_two_bounds(bound_op1, value1, opt_bound_op2, opt_value2)
        return x

    @classmethod
    def for_one_bound(cls, bound_op: str, value) -> RRange_:
        RRangeBoundFunctionEnumData_.check_bound_op_set_contains(
            bound_op, "bound_op", RRangeBoundFunctionEnumData_.ONE_BOUND_OP_SET)
        x = RRange_(cls.__PRIVATE_CTOR_KEY, bound_op, value)
        return x

    @classmethod
    def for_two_bounds(cls, bound_op1: str, value1, bound_op2: str, value2) -> RRange_:
        RRangeBoundFunctionEnumData_.check_bound_op_set_contains(
            bound_op1, "bound_op1", RRangeBoundFunctionEnumData_.TWO_BOUND_OP1_SET)
        RRangeBoundFunctionEnumData_.check_bound_op_set_contains(
            bound_op2, "bound_op2", RRangeBoundFunctionEnumData_.TWO_BOUND_OP2_SET)
        x = RRange_(cls.__PRIVATE_CTOR_KEY, bound_op1, value1, bound_op2, value2)
        return x

    def __init__(self,
                 private_ctor_key: int,
                 bound_op1: str,
                 value1,
                 bound_op2: str=None,
                 value2=None):
        if private_ctor_key != self.__PRIVATE_CTOR_KEY:
            raise ValueError("Private class constructor")
        self.__bound1 = self.__create_bound(bound_op1, "bound_op1", value1, "value1")
        self.__opt_bound2 = self.__create_bound(bound_op2, "bound_op2", value2, "value2")

    @classmethod
    def __create_bound(cls, bound_op: str, bound_op_arg_name: str, value, value_arg_name: str) -> RRangeBound_:
        if bound_op:
            RArgs.check_not_none(value, value_arg_name)
            x = cls.__get_op_func_enum(bound_op, bound_op_arg_name)
            y = RRangeBoundFunction_(x, value)
            z = RRangeBound_(y)
            return z
        else:
            return None

    @classmethod
    def __get_op_func_enum(cls, bound_op: str, bound_op_arg_name: str) -> RRangeBoundFunctionEnum_:
        try:
            x = RRange_.__BOUND_OP_TO_DATA_DICT[bound_op]
            return x
        except KeyError:
            raise ValueError("Argument '{}': Expect range bound operator as any of {}, but found: '{}'"
                             .format(bound_op_arg_name, RRange_.__BOUND_OP_TO_DATA_DICT.keys(), bound_op))

    def __contains__(self, item) -> bool:
        """ This is the membership operator: in """
        RArgs.check_not_none(item, "item")
        if isinstance(item, type(self)):
            #: :type item: RRange
            if not item.__bound1 in self.__bound1:
                return False
            if (not self.__opt_bound2) != (not item.__opt_bound2):
                return False
            x = item.__opt_bound2 in self.__opt_bound2
        else:
            if not item in self.__bound1:
                return False
            x = True
            if self.__opt_bound2:
                x = item in self.__opt_bound2
        return x

    def __eq__(self, other: RRange_) -> bool:
        if not isinstance(other, RRange_):
            return False
        x = (self.__bound1 == other.__bound1 and self.__opt_bound2 == other.__opt_bound2)
        return x

    def __hash__(self) -> int:
        x = hash((self.__bound1, self.__opt_bound2))
        return x

    def __str__(self) -> str:
        x = str(self.__bound1)
        if self.__opt_bound2:
            x += " and " + str(self.__opt_bound2)
        return x
