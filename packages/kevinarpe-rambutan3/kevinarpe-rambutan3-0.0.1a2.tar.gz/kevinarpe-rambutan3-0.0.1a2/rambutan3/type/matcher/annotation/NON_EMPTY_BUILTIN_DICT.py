from rambutan3.type.matcher.dict.RDictEnum import RDictEnum
from rambutan3.type.matcher.dict.RRangeSizeDictMatcher import RRangeSizeDictMatcher

NON_EMPTY_BUILTIN_DICT = RRangeSizeDictMatcher(RDictEnum.BUILTIN_DICT, min_size=1)
