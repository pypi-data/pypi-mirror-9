from rambutan3.type.matcher.cls_or_self.RAbstractClassOrSelfInstanceMatcher import RAbstractClassOrSelfInstanceMatcher


class RClassInstanceMatcher(RAbstractClassOrSelfInstanceMatcher):
    """Never use this class directly.  Instead, use: {@link CLS#CLS()}."""

    def __init__(self):
        super().__init__()

    # @override
    def matches(self, value) -> bool:
        x = isinstance(type(value), self._caller_class)
        return x

    # @override
    def __str__(self):
        x = "cls: {}".format(self._caller_class.__name__)
        return x
