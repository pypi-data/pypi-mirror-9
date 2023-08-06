from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum
from rambutan3.type.matcher.set.RSetOfMatcher import RSetOfMatcher


def BUILTIN_SET_OF(value_matcher: RAbstractTypeMatcher) -> RSetOfMatcher:
    x = RSetOfMatcher(RSetEnum.BUILTIN_SET, value_matcher)
    return x