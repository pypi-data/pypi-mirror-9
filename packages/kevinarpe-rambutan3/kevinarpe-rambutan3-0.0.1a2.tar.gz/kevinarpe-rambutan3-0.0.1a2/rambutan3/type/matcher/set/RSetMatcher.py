from rambutan3 import RArgs
from rambutan3.type.matcher.RInstanceMatcher import RInstanceMatcher
from rambutan3.type.matcher.set.RSetEnum import RSetEnum


class RSetMatcher(RInstanceMatcher):

    def __init__(self, set_enum: RSetEnum):
        RArgs.check_is_instance(set_enum, RSetEnum, "set_enum")
        super().__init__(*(set_enum.value))
