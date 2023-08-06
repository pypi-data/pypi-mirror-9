from rambutan3.type.matcher.range.RNumberRangeMatcher import RNumberRangeMatcher

RFloatRangeMatcher = None
class RFloatRangeMatcher(RNumberRangeMatcher):

    def __init__(self, bound_op1: str, value1: float, bound_op2: str=None, value2: float=None):
        super().__init__((float,), bound_op1, value1, bound_op2, value2)
