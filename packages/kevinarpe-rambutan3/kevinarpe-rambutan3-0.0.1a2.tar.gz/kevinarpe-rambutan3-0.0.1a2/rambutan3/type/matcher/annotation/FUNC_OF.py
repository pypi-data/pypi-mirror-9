from rambutan3.type.matcher.func.RFunctionSignatureMatcherBuilder import RFunctionSignatureMatcherBuilder


def FUNC_OF(*matcher_tuple) -> RFunctionSignatureMatcherBuilder:
    x = RFunctionSignatureMatcherBuilder(*matcher_tuple)
    return x
