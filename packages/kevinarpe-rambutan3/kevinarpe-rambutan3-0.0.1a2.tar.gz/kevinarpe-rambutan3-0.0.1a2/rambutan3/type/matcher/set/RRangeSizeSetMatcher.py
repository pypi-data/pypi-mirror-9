from rambutan3 import RArgs
from rambutan3.type.matcher.collection.RRangeSizeCollectionMatcher import RRangeSizeCollectionMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum


class RRangeSizeSetMatcher(RRangeSizeCollectionMatcher):

    def __init__(self, set_enum: RSetEnum, *, min_size: int=-1, max_size: int=-1):
        RArgs.check_is_instance(set_enum, RSetEnum, "set_enum")
        super().__init__(set_enum.value, min_size=min_size, max_size=max_size)
