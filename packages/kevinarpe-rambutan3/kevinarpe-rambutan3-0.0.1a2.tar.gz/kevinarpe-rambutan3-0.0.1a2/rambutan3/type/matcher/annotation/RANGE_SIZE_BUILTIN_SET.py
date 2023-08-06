from rambutan3.type.matcher.set.RRangeSizeSetMatcher import RRangeSizeSetMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum

__author__ = 'kca'


def RANGE_SIZE_BUILTIN_SET(*, min_size: int=-1, max_size: int=-1) -> RRangeSizeSetMatcher:
    x = RRangeSizeSetMatcher(RSetEnum.BUILTIN_SET, min_size=min_size, max_size=max_size)
    return x