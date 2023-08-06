from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.seq.RRangeSizeSequenceOfMatcher import RRangeSizeSequenceOfMatcher
from rambutan3.type.matcher.seq.RSequenceEnum import RSequenceEnum

__author__ = 'kca'


def NON_EMPTY_TUPLE_OF(value_matcher: RAbstractTypeMatcher) -> RRangeSizeSequenceOfMatcher:
    x = RRangeSizeSequenceOfMatcher(RSequenceEnum.TUPLE, value_matcher, min_size=1)
    return x