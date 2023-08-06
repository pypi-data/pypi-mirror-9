from rambutan3.type.matcher.set.RRangeSizeSetMatcher import RRangeSizeSetMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum

NON_EMPTY_BUILTIN_FROZENSET = RRangeSizeSetMatcher(RSetEnum.BUILTIN_FROZENSET, min_size=1)
