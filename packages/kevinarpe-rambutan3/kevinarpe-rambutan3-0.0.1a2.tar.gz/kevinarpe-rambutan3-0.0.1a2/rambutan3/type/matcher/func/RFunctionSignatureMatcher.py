import inspect
from rambutan3 import RArgs
from rambutan3.type import RTypes
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.RInstanceMatcher import RInstanceMatcher


RFunctionSignatureMatcher = None
class RFunctionSignatureMatcher(RInstanceMatcher):

    def __init__(self, param_matcher_tuple: tuple, opt_return_matcher: RAbstractTypeMatcher=None):
        """
        :param param_matcher_tuple: list of RAbstractValueChecker
        :param opt_return_matcher: if None, this is a subroutine, not a function
        """
        super().__init__(*(RTypes.FUNCTION_TYPE_TUPLE))
        RArgs.check_not_none(param_matcher_tuple, "param_matcher_tuple")

        for index, param_matcher in enumerate(param_matcher_tuple):
            RArgs.check_is_instance(param_matcher, RAbstractTypeMatcher, "param_matcher_tuple[{}]", index)

        if opt_return_matcher is not None:
            RArgs.check_is_instance(opt_return_matcher, RAbstractTypeMatcher, "opt_return_matcher")

        self.__param_matcher_tuple = param_matcher_tuple
        self.__opt_return_matcher = opt_return_matcher

    # @override
    def matches(self, func: RTypes.FUNCTION_TYPE_TUPLE) -> bool:
        if not super().matches(func):
            return False
        #: :type: Signature
        sig = inspect.signature(func)
        #: :type: dict of (str, Parameter)
        name_to_param_dict = sig.parameters
        if len(name_to_param_dict) != len(self.__param_matcher_tuple):
            return False

        #: :type param: Parameter
        for index, param in enumerate(name_to_param_dict.values()):
            actual_matcher = param.annotation
            #: :type: RAbstractTypeMatcher
            expected_matcher = self.__param_matcher_tuple[index]
            if expected_matcher != actual_matcher:
                return False

        if sig.return_annotation is not None and self.__opt_return_matcher is not None:
            x = (sig.return_annotation == self.__opt_return_matcher)
            return x
        else:
            # False if exactly one has return annotation.
            x = (sig.return_annotation is None) != (self.__opt_return_matcher is None)
            return x

    # @override
    def __eq__(self, other: RFunctionSignatureMatcher) -> bool:
        if not isinstance(other, RFunctionSignatureMatcher):
            return False
        if not super().__eq__(other):
            return False
        x = (self.__opt_return_matcher == other.__opt_return_matcher
             and self.__param_matcher_tuple == other.__param_matcher_tuple)
        return x

    # @override
    def __hash__(self) -> int:
        # Ref: http://stackoverflow.com/questions/29435556/how-to-combine-hash-codes-in-in-python3
        super_hash = super().__hash__()
        self_hash = hash((self.__param_matcher_tuple, self.__opt_return_matcher))
        x = super_hash ^ self_hash
        return x

    # @override
    def __str__(self) -> str:
        args = " , ".join(self.__param_matcher_tuple)
        x = "def *({})".format(args)
        if self.__opt_return_matcher:
            x += " -> {}".format(self.__opt_return_matcher)
        return x
