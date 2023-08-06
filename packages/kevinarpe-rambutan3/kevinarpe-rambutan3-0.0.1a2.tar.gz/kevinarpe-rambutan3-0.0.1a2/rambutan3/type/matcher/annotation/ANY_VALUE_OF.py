from rambutan3.type.matcher.RAnyValueOfMatcher import RAnyValueOfMatcher


def ANY_VALUE_OF(*value_tuple) -> RAnyValueOfMatcher:
    x = RAnyValueOfMatcher(*value_tuple)
    return x
