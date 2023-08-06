from rambutan3.type.matcher.set.RRangeSizeSetMatcher import RRangeSizeSetMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum

NON_EMPTY_BUILTIN_SET = RRangeSizeSetMatcher(RSetEnum.BUILTIN_SET, min_size=1)
