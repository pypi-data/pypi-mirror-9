"""Base classes for value matching

@author Kevin Connor ARPE (kevinarpe@gmail.com)
"""

from abc import abstractmethod, ABCMeta

from rambutan3 import RArgs
from rambutan3.type.matcher.error.RCheckArgsError import RCheckArgsError
from rambutan3.type.matcher.error.RCheckArgsErrorFormatter import RCheckArgsErrorFormatter


RAbstractTypeMatcher = None
# Ref: https://docs.python.org/3/library/abc.html#abc.abstractmethod
# Using this decorator requires that the class’s metaclass is ABCMeta or is derived from it.
class RAbstractTypeMatcher(metaclass=ABCMeta):
    """Abstract base class for all type matchers, include type matchers."""

    @abstractmethod
    def matches(self, value) -> bool:
        """Tests if value matches

        Example: if matcher requires an instance of type {@code str}, then {@code "abc"} will return {@code True}.

        @param value
               value to test / match / check

        @return {@code True} if value matches, else {@code False}
        """
        raise NotImplementedError()

    def check(self,
              value,
              error_formatter: RCheckArgsErrorFormatter=RCheckArgsErrorFormatter(),
              *args,
              **kwargs):
        """Checks if a value matches this matcher ({@code self})

        @param value
               value to test
        @param error_formatter (optional: RCheckArgsErrorFormatter)
               generates an exception message if test fails
        @param *args
               passed directly to {@code error_formatter.format()}
        @param **kwargs
               passed directly to {@code error_formatter.format()}

        @throws RCheckArgsError
                if test fails
        """
        if not self.matches(value):
            x = error_formatter.format(self, value, *args, **kwargs)
            raise RCheckArgsError(x)

    def __or__(self, other: RAbstractTypeMatcher) -> RAbstractTypeMatcher:
        """operator|: Combines {@code self} with {@code other} to create logical OR type matcher

        @param other
               another type matcher

        @return new logical OR type matcher

        @see RLogicalOrValueMatcher
        """

        x = RLogicalOrTypeMatcher(self, other)
        return x

    @abstractmethod
    def __eq__(self, other: RAbstractTypeMatcher) -> bool:
        """operator==: Compares {@code self} with {@code other}

        param other
              another type matcher

        @return False if {@code other} is not type {@code RAbstractTypeMatcher}
                Else, result of type matcher equality test

        """
        pass

    # Accordingly, when defining __eq__(), one should also define __ne__() so that the operators will behave as expected.
    # Ref: https://docs.python.org/3/reference/datamodel.html
    def __ne__(self, other: RAbstractTypeMatcher) -> bool:
        x = not (self == other)
        return x

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass


RLogicalOrTypeMatcher = None
class RLogicalOrTypeMatcher(RAbstractTypeMatcher):
    """Combines two or more type matchers to create a unified logical OR type matcher

    This class is fully tested.
    """

    def __init__(self,
                 left: (RAbstractTypeMatcher, RLogicalOrTypeMatcher),
                 right: (RAbstractTypeMatcher, RLogicalOrTypeMatcher)):
        """Never call this ctor directly; instead use operator|: {@link RValueMatcher#__or__()}

        @param left
               first type matcher; logical OR type matchers are handled correctly
        @param right
               second type matcher; logical OR type matchers are handled correctly

        @return new type matcher that combines first and second type matcher as logical OR type matcher
        """
        super().__init__()
        RArgs.check_is_instance(left, RAbstractTypeMatcher, "left")
        RArgs.check_is_instance(right, RAbstractTypeMatcher, "right")

        matcher_list = []
        if isinstance(left, RLogicalOrTypeMatcher):
            matcher_list.extend(left.__matcher_tuple)
        else:
            matcher_list.append(left)

        if isinstance(right, RLogicalOrTypeMatcher):
            matcher_list.extend(right.__matcher_tuple)
        else:
            matcher_list.append(right)

        self.__matcher_tuple = tuple(matcher_list)
        self.__matcher_frozenset = frozenset(matcher_list)

    # @override
    def matches(self, value) -> bool:
        # Ref: http://stackoverflow.com/q/5217489/257299
        x = any(y.matches(value) for y in self.__matcher_tuple)
        return x

    def __iter__(self):
        """Iterates internal list of type matchers"""
        x = iter(self.__matcher_tuple)
        return x

    # @override
    def __eq__(self, other: RLogicalOrTypeMatcher) -> bool:
        if not isinstance(other, RLogicalOrTypeMatcher):
            return False
        x = (self.__matcher_frozenset == other.__matcher_frozenset)
        return x

    # @override
    def __hash__(self) -> int:
        x = hash(self.__matcher_frozenset)
        return x

    # @override
    def __str__(self):
        x = " | ".join([str(x) for x in self.__matcher_tuple])
        return x
