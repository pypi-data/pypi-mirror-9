import enum
import operator
from rambutan3 import RArgs
from rambutan3.type.REnum import REnum
from rambutan3.type.matcher.range.RRangeBoundFunctionEnumData_ import RRangeBoundFunctionEnumData_


@enum.unique
class RRangeBoundFunctionEnum_(REnum):
    """
    This class exists only to be used by matchers.
    """

    # def __init__(self, data: RRangeBoundFunctionEnumData_):
    #     # Enable this code to blowup at runtime.  No idea why this same error does not affect RTypedEnum
    #     #super(RRangeBoundFunctionEnum_, self).__init__()
    #     #: :type: RRangeBoundFunctionEnumData_
    #     self.__data = RArgs.check_not_none(data, "data")
    #
    # @property
    # def data(self) -> RRangeBoundFunctionEnumData_:
    #     return self.__data

    GREATER = \
        RRangeBoundFunctionEnumData_('>', operator.gt)
    GREATER_EQUAL = \
        RRangeBoundFunctionEnumData_('>=', operator.ge)
    LESS = \
        RRangeBoundFunctionEnumData_('<', operator.lt)
    LESS_EQUAL = \
        RRangeBoundFunctionEnumData_('<=', operator.le)
