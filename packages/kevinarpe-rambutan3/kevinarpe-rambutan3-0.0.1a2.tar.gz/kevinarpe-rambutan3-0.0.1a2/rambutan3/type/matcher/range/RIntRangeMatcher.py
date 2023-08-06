from rambutan3.type.matcher.range.RNumberRangeMatcher import RNumberRangeMatcher

RIntRangeMatcher = None
class RIntRangeMatcher(RNumberRangeMatcher):

    def __init__(self, bound_op1: str, value1: int, bound_op2: str=None, value2: int=None):
        super().__init__((int,), bound_op1, value1, bound_op2, value2)
