from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.set.RRangeSizeSetOfMatcher import RRangeSizeSetOfMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum

__author__ = 'kca'


def NON_EMPTY_BUILTIN_FROZENSET_OF(value_matcher: RAbstractTypeMatcher) -> RRangeSizeSetOfMatcher:
    x = RRangeSizeSetOfMatcher(RSetEnum.BUILTIN_FROZENSET, value_matcher, min_size=1)
    return x