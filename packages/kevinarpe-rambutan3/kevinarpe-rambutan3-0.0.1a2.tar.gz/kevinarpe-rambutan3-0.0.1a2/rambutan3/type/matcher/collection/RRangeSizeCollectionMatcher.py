from rambutan3 import RArgs
from rambutan3.type.matcher.RInstanceMatcher import RInstanceMatcher


RRangeSizeCollectionMatcher = None
class RRangeSizeCollectionMatcher(RInstanceMatcher):

    def __init__(self, class_or_type_tuple: tuple, *, min_size: int=-1, max_size: int=-1):
        RArgs.check_is_instance(class_or_type_tuple, tuple, "class_or_type_tuple")
        super().__init__(*class_or_type_tuple)
        self.__check_sizes(min_size=min_size, max_size=max_size)
        self.__min_size = min_size
        self.__max_size = max_size

    @staticmethod
    def __check_sizes(*, min_size: int, max_size: int):
        RArgs.check_is_instance(min_size, int, "min_size")
        RArgs.check_is_instance(max_size, int, "max_size")
        if -1 == min_size and -1 == max_size:
            raise ValueError("Both args 'min_size' and 'max_size' are -1")
        if min_size < -1:
            raise ValueError("Arg 'min_size' must be >= -1: {}".format(min_size))
        if max_size < -1:
            raise ValueError("Arg 'max_size' must be >= -1: {}".format(max_size))
        if -1 != min_size and -1 != max_size and min_size > max_size:
            raise ValueError("Arg 'min_size' > arg 'max_size': {} > {}".format(min_size, max_size))

    # @override
    def matches(self, collection) -> bool:
        if not super().matches(collection):
            return False
        L = len(collection)
        if -1 != self.__min_size and L < self.__min_size:
            return False
        if -1 != self.__max_size and L > self.__max_size:
            return False
        return True

    # @override
    def __eq__(self, other: RRangeSizeCollectionMatcher) -> bool:
        if not isinstance(other, RRangeSizeCollectionMatcher):
            return False
        if not super().__eq__(other):
            return False
        x = (self.__min_size == other.__min_size and self.__max_size == other.__max_size)
        return x

    # @override
    def __hash__(self) -> int:
        # Ref: http://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
        super_hash = super().__hash__()
        self_hash = hash((self.__min_size, self.__max_size))
        x = super_hash ^ self_hash
        return x

    # @override
    def __str__(self):
        suffix = ""
        if -1 != self.__min_size:
            suffix = "size >= {}".format(self.__min_size)
        if -1 != self.__max_size:
            if suffix:
                suffix += " and "
            suffix = "size <= {}".format(self.__max_size)
        x = super().__str__() + " where " + suffix
        return x
