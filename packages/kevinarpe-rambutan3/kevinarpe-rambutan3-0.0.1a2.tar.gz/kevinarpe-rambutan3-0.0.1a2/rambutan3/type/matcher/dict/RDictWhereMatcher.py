from rambutan3 import RArgs
from rambutan3.container.frozendict import frozendict
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.dict.RDictEnum import RDictEnum
from rambutan3.type.matcher.dict.RDictMatcher import RDictMatcher
from rambutan3.type.string import RStrUtil


RDictWhereMatcher = None
class RDictWhereMatcher(RDictMatcher):

    def __init__(self, dict_enum: RDictEnum, matcher_dict: dict, *, is_exact: bool):
        super().__init__(dict_enum)
        RArgs.check_is_instance(matcher_dict, dict, "matcher_dict")
        RArgs.check_is_instance(is_exact, bool, "is_exact")

        for key, value_matcher in matcher_dict.items():
            RArgs.check_is_instance(value_matcher, RAbstractTypeMatcher, "value_matcher for key '{}'", key)

        self.__matcher_dict = frozendict(matcher_dict)
        self.__is_exact = is_exact

    # @override
    def matches(self, d: dict) -> bool:
        if not super().matches(d):
            return False

#        dict_copy = copy.deepcopy(d)
        """:type: dict"""
        dict_copy = d.copy()

        for key, value_matcher in self.__matcher_dict.items():
            value = dict_copy.get(key)
            if not value_matcher.matches(value):
                return False
            del dict_copy[key]

        if self.__is_exact and dict_copy:
            return False
        return True

    # @override
    def __eq__(self, other: RDictWhereMatcher) -> bool:
        if not isinstance(other, RDictWhereMatcher):
            return False
        if not super().__eq__(other):
            return False
        x = (self.__is_exact == other.__is_exact and self.__matcher_dict == other.__matcher_dict)
        return x

    # @override
    def __hash__(self) -> int:
        # Ref: http://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
        super_hash = super().__hash__()
        self_hash = hash((self.__is_exact, self.__matcher_dict))
        x = super_hash ^ self_hash
        return x

    # @override
    def __str__(self):
        where_clause = "EXACTLY" if self.__is_exact else "AT LEAST"
        matcher_dict_str = \
            "{" \
            + ", ".join(
                [
                    RStrUtil.auto_quote(key) + ": " + RStrUtil.auto_quote(value)
                    for key, value in self.__matcher_dict.items()
                ]) \
            + "}"
        x = "{} where {} {}".format(super().__str__(), where_clause, matcher_dict_str)
        return x
