from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum
from rambutan3.type.matcher.set.RSetOfMatcher import RSetOfMatcher

__author__ = 'kca'


def BUILTIN_FROZENSET_OF(value_matcher: RAbstractTypeMatcher) -> RSetOfMatcher:
    x = RSetOfMatcher(RSetEnum.BUILTIN_FROZENSET, value_matcher)
    return x