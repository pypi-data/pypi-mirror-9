from _collections_abc import Iterable
from rambutan3 import RArgs
from rambutan3.type.matcher.RInstanceMatcher import RInstanceMatcher
from rambutan3.type.matcher.range.RRange_ import RRange_

RNumberRangeMatcher = None
class RNumberRangeMatcher(RInstanceMatcher):

    __ALLOWED_TYPE_TUPLE = (int, float)

    def __init__(self,
                 class_or_type_seq: (tuple, list, Iterable),
                 bound_op1: str,
                 value1: (int, float),
                 bound_op2: str=None,
                 value2: (int, float)=None):
        self.__check_class_or_type_seq(class_or_type_seq)
        super().__init__(*class_or_type_seq)
        RArgs.check_is_instance(value1, class_or_type_seq, "value1")
        if value2:
            RArgs.check_is_instance(value2, class_or_type_seq, "value2")
        self.__range = RRange_.create(bound_op1, value1, bound_op2, value2)

    def __check_class_or_type_seq(self, class_or_type_seq: (tuple, list, Iterable)):
        RArgs.check_iterable_not_empty_and_items_not_none(class_or_type_seq, "class_or_type_seq")
        for class_or_type in class_or_type_seq:
            if class_or_type not in self.__ALLOWED_TYPE_TUPLE:
                raise ValueError("Class or type {} is not allowed: {}"
                                 .format(class_or_type.__name__, ", ".join(self.__ALLOWED_TYPE_TUPLE)))

    # @override
    def matches(self, value: (int, float)) -> bool:
        if not super().matches(value):
            return False
        x = (value in self.__range)
        return x

    # @override
    def __eq__(self, other: RNumberRangeMatcher) -> bool:
        if not isinstance(other, RNumberRangeMatcher):
            return False
        if not super().__eq__(other):
            return False
        x = (self.__range == other.__range)
        return x

    # @override
    def __hash__(self) -> int:
        # Ref: http://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
        super_hash = super().__hash__()
        self_hash = hash(self.__range)
        x = super_hash ^ self_hash
        return x

    # @override
    def __str__(self):
        x = "{}: {}".format(super().__str__(), self.__range)
        return x
