from _collections_abc import Mapping, MutableMapping
from rambutan3.container.frozendict import frozendict
from rambutan3.container.hashabledict import hashabledict
from rambutan3.type.REnum import REnum


class RDictEnum(REnum):

    BUILTIN_DICT = (dict,)
    DICT = (dict, hashabledict, frozendict, Mapping, MutableMapping)
