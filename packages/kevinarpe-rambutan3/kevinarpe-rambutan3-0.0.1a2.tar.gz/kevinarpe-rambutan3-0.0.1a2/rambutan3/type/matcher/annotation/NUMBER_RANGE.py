from rambutan3.type.matcher.RCheckArgs import check_args
from rambutan3.type.matcher.annotation.ANY_VALUE_OF import ANY_VALUE_OF
from rambutan3.type.matcher.annotation.INSTANCE_OF import INSTANCE_OF
from rambutan3.type.matcher.annotation.NUMBER import NUMBER
from rambutan3.type.matcher.annotation.NONE import NONE
from rambutan3.type.matcher.range.RNumberRangeMatcher import RNumberRangeMatcher
from rambutan3.type.matcher.range.RRangeBoundFunctionEnumData_ import RRangeBoundFunctionEnumData_

__RANGE_BOUND_OP1 = ANY_VALUE_OF(*RRangeBoundFunctionEnumData_.ONE_BOUND_OP_SET)
__RANGE_BOUND_OP2 = ANY_VALUE_OF(*RRangeBoundFunctionEnumData_.TWO_BOUND_OP2_SET)

@check_args
def NUMBER_RANGE(bound1: __RANGE_BOUND_OP1,
                 value1: NUMBER,
                 bound2: __RANGE_BOUND_OP2 | NONE=None,
                 value2: NUMBER | NONE=None) \
        -> INSTANCE_OF(RNumberRangeMatcher):
    x = RNumberRangeMatcher((int, float), bound1, value1, bound2, value2)
    return x
