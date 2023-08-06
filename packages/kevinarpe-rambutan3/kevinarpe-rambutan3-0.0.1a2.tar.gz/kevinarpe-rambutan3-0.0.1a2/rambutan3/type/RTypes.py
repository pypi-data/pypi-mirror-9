import re
import types

REGEX_PATTERN_TYPE = type(re.compile(''))
REGEX_MATCH_TYPE = type(re.compile('').match(''))
FUNCTION_TYPE_TUPLE = (types.FunctionType, types.BuiltinFunctionType)
NUMBER_TYPE_TUPLE = (int, float)
