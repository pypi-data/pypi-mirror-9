from rambutan3.type.matcher.dict.RDictEnum import RDictEnum
from rambutan3.type.matcher.dict.RDictWhereMatcher import RDictWhereMatcher


def BUILTIN_DICT_WHERE_AT_LEAST(matcher_dict: dict) -> RDictWhereMatcher:
    x = RDictWhereMatcher(RDictEnum.BUILTIN_DICT, matcher_dict, is_exact=False)
    return x