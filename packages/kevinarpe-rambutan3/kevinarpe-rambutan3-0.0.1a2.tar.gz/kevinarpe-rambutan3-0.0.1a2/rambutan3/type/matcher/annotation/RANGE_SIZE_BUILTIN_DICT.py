from rambutan3.type.matcher.dict.RDictEnum import RDictEnum
from rambutan3.type.matcher.dict.RRangeSizeDictMatcher import RRangeSizeDictMatcher

__author__ = 'kca'


def RANGE_SIZE_BUILTIN_DICT(*, min_size: int=-1, max_size: int=-1) -> RRangeSizeDictMatcher:
    x = RRangeSizeDictMatcher(RDictEnum.BUILTIN_DICT, min_size=min_size, max_size=max_size)
    return x