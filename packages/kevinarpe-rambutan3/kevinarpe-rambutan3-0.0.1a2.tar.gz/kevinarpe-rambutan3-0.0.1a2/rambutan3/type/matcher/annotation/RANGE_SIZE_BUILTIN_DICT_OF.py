from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.dict.RDictEnum import RDictEnum
from rambutan3.type.matcher.dict.RRangeSizeDictOfMatcher import RRangeSizeDictOfMatcher

__author__ = 'kca'


def RANGE_SIZE_BUILTIN_DICT_OF(*,
                               key_matcher: RAbstractTypeMatcher=None,
                               value_matcher: RAbstractTypeMatcher=None,
                               min_size: int=-1, max_size: int=-1) -> RRangeSizeDictOfMatcher:
    x = RRangeSizeDictOfMatcher(RDictEnum.BUILTIN_DICT,
                                key_matcher=key_matcher,
                                value_matcher=value_matcher,
                                min_size=min_size,
                                max_size=max_size)
    return x