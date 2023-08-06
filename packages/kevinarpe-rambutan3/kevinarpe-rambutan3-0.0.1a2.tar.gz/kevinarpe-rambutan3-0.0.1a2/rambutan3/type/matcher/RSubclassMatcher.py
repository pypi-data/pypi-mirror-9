from rambutan3 import RArgs
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher


RSubclassMatcher = None
class RSubclassMatcher(RAbstractTypeMatcher):
    """Type and (sub)class matcher

    Example:
    class X: pass
    class Y(X): pass
    True : X is a subclass of X.
    True : Y is a subclass of X.
    False: X is a subclass of Y.

    TODO: This class is fully tested.

    @author Kevin Connor ARPE (kevinarpe@gmail.com)

    @see builtins#issubclass()
    """

    def __init__(self, type_or_class: type):
        super().__init__()
        RArgs.check_is_instance(type_or_class, type, "type_or_class")
        self.__type = type_or_class

    # @override
    def matches(self, value) -> bool:
        try:
            x = issubclass(value, self.__type)
            return x
        except:
            return False

    # @override
    def __eq__(self, other: RSubclassMatcher) -> bool:
        if not isinstance(other, RSubclassMatcher):
            return False
        x = (self.__type == other.__type)
        return x

    # @override
    def __hash__(self) -> int:
        x = hash(self.__type)
        return x

    # @override
    def __str__(self):
        x = "subclass of {}".format(self.__type.__name__)
        return x
