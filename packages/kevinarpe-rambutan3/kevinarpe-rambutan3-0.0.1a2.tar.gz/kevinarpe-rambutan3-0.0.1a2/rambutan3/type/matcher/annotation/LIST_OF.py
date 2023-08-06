from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.seq.RSequenceEnum import RSequenceEnum
from rambutan3.type.matcher.seq.RSequenceOfMatcher import RSequenceOfMatcher


def LIST_OF(value_matcher: RAbstractTypeMatcher) -> RSequenceOfMatcher:
    x = RSequenceOfMatcher(RSequenceEnum.LIST, value_matcher)
    return x