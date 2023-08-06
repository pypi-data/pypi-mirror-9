import operator
import types
from rambutan3 import RArgs
from rambutan3.type import RTypes


RRangeBoundFunctionEnumData_ = None
class RRangeBoundFunctionEnumData_:
    """This class exists only to be used by matchers."""

    # The first bound may be lower or upper; allow either.
    ONE_BOUND_OP_SET = {'>', '>=', '<', '<='}
    TWO_BOUND_OP1_SET = {'>', '>='}
    TWO_BOUND_OP2_SET = {'<', '<='}

    @classmethod
    def check_bound_op_set_contains(cls, op: str, op_arg_name: str, op_set: set):
        RArgs.check_is_instance(op, str, op_arg_name)
        if op not in op_set:
            raise ValueError("Argument '{}': Expected one of {}, but found '{}'".format(op_arg_name, op_set, op))

    def __init__(self, op: str, op_func: RTypes.FUNCTION_TYPE_TUPLE):
        RArgs.check_is_instance(op, str, "op")
        self.check_bound_op_set_contains(op, "op", self.ONE_BOUND_OP_SET)
        self.__op = op
        #: :type: types.FunctionType
        RArgs.check_is_instance(op_func, RTypes.FUNCTION_TYPE_TUPLE, "op_func")
        self.__op_func = op_func

    @property
    def op(self) -> str:
        return self.__op

    @property
    def op_func(self) -> types.FunctionType:
        return self.__op_func

    @property
    def is_greater(self) -> bool:
        x = (self.__op_func is operator.gt) or (self.__op_func is operator.ge)
        return x

    @property
    def is_inclusive(self) -> bool:
        x = (self.__op_func is operator.ge) or (self.__op_func is operator.le)
        return x

    def __eq__(self, other: RRangeBoundFunctionEnumData_) -> bool:
        if not isinstance(other, RRangeBoundFunctionEnumData_):
            return False
        x = (self.__op == other.__op and self.__op_func == other.__op_func)
        return x

    def __hash__(self) -> int:
        x = hash((self.__op, self.__op_func))
        return x

    def __str__(self):
        return self.__op
