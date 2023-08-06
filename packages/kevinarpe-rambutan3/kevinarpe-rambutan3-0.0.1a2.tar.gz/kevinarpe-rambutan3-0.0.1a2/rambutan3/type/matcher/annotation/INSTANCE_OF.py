from functools import lru_cache
from rambutan3.type.matcher.RInstanceMatcher import RInstanceMatcher


@lru_cache(maxsize=None)
def INSTANCE_OF(type_or_class: type) -> RInstanceMatcher:
    x = RInstanceMatcher(type_or_class)
    return x