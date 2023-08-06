from functools import lru_cache
from rambutan3.type.matcher.RSubclassMatcher import RSubclassMatcher


@lru_cache(maxsize=None)
def SUBCLASS_OF(type_or_class: type) -> RSubclassMatcher:
    x = RSubclassMatcher(type_or_class)
    return x