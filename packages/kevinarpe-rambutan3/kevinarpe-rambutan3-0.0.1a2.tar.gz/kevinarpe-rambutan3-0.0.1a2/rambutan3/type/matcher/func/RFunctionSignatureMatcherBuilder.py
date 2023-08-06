from rambutan3 import RArgs
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.func.RFunctionSignatureMatcher import RFunctionSignatureMatcher


class RFunctionSignatureMatcherBuilder:

    def __init__(self, *param_matcher_tuple):
        for index, value in enumerate(param_matcher_tuple):
            RArgs.check_is_instance(value, RAbstractTypeMatcher, "Arg#{}", 1 + index)
        self.__param_matcher_tuple = param_matcher_tuple

    def returns(self, return_matcher: RAbstractTypeMatcher) -> RFunctionSignatureMatcher:
        x = RFunctionSignatureMatcher(param_matcher_tuple=self.__param_matcher_tuple,
                                      opt_return_matcher=return_matcher)
        return x

    def returnsNothing(self) -> RFunctionSignatureMatcher:
        x = RFunctionSignatureMatcher(param_matcher_tuple=self.__param_matcher_tuple)
        return x

    def matches(self, dummy):
        raise TypeError("Type matcher incomplete: Must first call returns() or returnsNothing()")
