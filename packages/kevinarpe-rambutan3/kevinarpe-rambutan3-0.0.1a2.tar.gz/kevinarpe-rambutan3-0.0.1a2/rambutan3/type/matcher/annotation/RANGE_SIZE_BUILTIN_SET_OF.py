from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.set.RRangeSizeSetOfMatcher import RRangeSizeSetOfMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum

__author__ = 'kca'


def RANGE_SIZE_BUILTIN_SET_OF(value_matcher: RAbstractTypeMatcher, *, min_size: int=-1, max_size: int=-1) \
        -> RRangeSizeSetOfMatcher:
    x = RRangeSizeSetOfMatcher(RSetEnum.BUILTIN_SET, value_matcher, min_size=min_size, max_size=max_size)
    return x