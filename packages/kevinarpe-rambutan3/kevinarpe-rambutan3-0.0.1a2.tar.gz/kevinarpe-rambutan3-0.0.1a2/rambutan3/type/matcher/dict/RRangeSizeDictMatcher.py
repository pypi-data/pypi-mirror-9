from rambutan3 import RArgs
from rambutan3.type.matcher.collection.RRangeSizeCollectionMatcher import RRangeSizeCollectionMatcher
from rambutan3.type.matcher.dict.RDictEnum import RDictEnum


class RRangeSizeDictMatcher(RRangeSizeCollectionMatcher):

    def __init__(self, dict_enum: RDictEnum, *, min_size: int=-1, max_size: int=-1):
        RArgs.check_is_instance(dict_enum, RDictEnum, "dict_enum")
        super().__init__(dict_enum.value, min_size=min_size, max_size=max_size)
