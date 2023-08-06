from rambutan3 import RArgs
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.seq.RSequenceEnum import RSequenceEnum
from rambutan3.type.matcher.seq.RSequenceMatcher import RSequenceMatcher


RSequenceOfMatcher = None
class RSequenceOfMatcher(RSequenceMatcher):

    def __init__(self, sequence_enum: RSequenceEnum, element_matcher: RAbstractTypeMatcher):
        super().__init__(sequence_enum)
        RArgs.check_is_instance(element_matcher, RAbstractTypeMatcher, "element_matcher")
        self.__element_matcher = element_matcher

    # @override
    def matches(self, seq) -> bool:
        if not super().matches(seq):
            return False
        x = all(self.__element_matcher.matches(y) for y in seq)
        return x

    # @override
    def __eq__(self, other: RSequenceOfMatcher) -> bool:
        if not isinstance(other, RSequenceOfMatcher):
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
