from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher


RAnyTypeMatcher = None
class RAnyTypeMatcher(RAbstractTypeMatcher):

    def __init__(self):
        super().__init__()

    # @override
    def matches(self, value) -> bool:
        x = value is not None
        return x

    # @override
    def __eq__(self, other: RAnyTypeMatcher) -> bool:
        x = isinstance(other, RAnyTypeMatcher)
        return x

    # @override
    def __hash__(self) -> int:
        x = super().__hash__()
        return x

    # @override
    def __str__(self):
        return "any non-None value"
