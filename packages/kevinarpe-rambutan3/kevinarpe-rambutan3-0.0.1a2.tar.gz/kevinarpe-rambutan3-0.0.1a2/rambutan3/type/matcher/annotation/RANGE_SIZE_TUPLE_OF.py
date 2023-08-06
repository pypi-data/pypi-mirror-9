from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.seq.RRangeSizeSequenceOfMatcher import RRangeSizeSequenceOfMatcher
from rambutan3.type.matcher.seq.RSequenceEnum import RSequenceEnum

__author__ = 'kca'


def RANGE_SIZE_TUPLE_OF(value_matcher: RAbstractTypeMatcher, *, min_size: int=-1, max_size: int=-1) \
        -> RRangeSizeSequenceOfMatcher:
    x = RRangeSizeSequenceOfMatcher(RSequenceEnum.TUPLE, value_matcher, min_size=min_size, max_size=max_size)
    return x