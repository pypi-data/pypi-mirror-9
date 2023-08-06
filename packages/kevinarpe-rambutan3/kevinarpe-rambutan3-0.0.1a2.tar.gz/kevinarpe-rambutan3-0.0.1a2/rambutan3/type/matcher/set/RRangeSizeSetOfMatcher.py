from rambutan3 import RArgs
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.set.RRangeSizeSetMatcher import RRangeSizeSetMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum


RRangeSizeSetOfMatcher = None
class RRangeSizeSetOfMatcher(RRangeSizeSetMatcher):

    def __init__(self,
                 set_enum: RSetEnum,
                 element_matcher: RAbstractTypeMatcher,
                 *,
                 min_size: int=-1,
                 max_size: int=-1):
        super().__init__(set_enum, min_size=min_size, max_size=max_size)
        RArgs.check_is_instance(element_matcher, RAbstractTypeMatcher, "element_matcher")
        self.__element_matcher = element_matcher

    # @override
    def matches(self, collection) -> bool:
        if not super().matches(collection):
            return False
        x = all(self.__element_matcher.matches(y) for y in collection)
        return x

    # @override
    def __eq__(self, other: RRangeSizeSetOfMatcher) -> bool:
        if not isinstance(other, RRangeSizeSetOfMatcher):
            return False
        if not super().__eq__(other):
            return False
        x = (self.__element_matcher == other.__element_matcher)
        return x

    # @override
    def __hash__(self) -> int:
        # Ref: http://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
        super_hash = super().__hash__()
        self_hash = hash(self.__element_matcher)
        x = super_hash ^ self_hash
        return x

    # @override
    def __str__(self):
        x = "{} of [{}]".format(super().__str__(), self.__element_matcher)
        return x
