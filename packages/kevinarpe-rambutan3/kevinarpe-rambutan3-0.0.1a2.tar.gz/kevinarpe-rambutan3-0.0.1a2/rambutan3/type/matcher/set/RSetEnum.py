from _collections_abc import Set, MutableSet
from rambutan3.container.hashableset import hashableset
from rambutan3.type.REnum import REnum


class RSetEnum(REnum):

    BUILTIN_SET = (set,)
    BUILTIN_FROZENSET = (frozenset,)
    SET = (set, hashableset, frozenset, Set, MutableSet)
