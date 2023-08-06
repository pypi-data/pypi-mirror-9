from rambutan3 import RArgs
from rambutan3.type import RTypes
from rambutan3.type.string.RStringDelegator import RStringDelegator


class RPatternText(RStringDelegator):
    """
    Wraps a {@link str} value that matches a regular expression.

    Examples: email address, telephone number, or postal code

    This class is fully tested.

    @author Kevin Connor ARPE (kevinarpe@gmail.com)
    """

    def __init__(self, value: str, regex_pattern: RTypes.REGEX_PATTERN_TYPE):
        """
        @param value
               any string that matches regular expression in {@code regex_pattern}
        @param regex_pattern
               regular expression to restrict valid string values

        @throws TypeError
                if {@code value} is not type {@link str}
                if {@code regex_pattern} is not a regular expression pattern
        @throws ValueError
                if {@code value} does not match regular expression in {@code regex_pattern}

        @see re#compile()
        """
        super().__init__(value)
        RArgs.check_is_instance(regex_pattern, RTypes.REGEX_PATTERN_TYPE, "regex_pattern")
        if not regex_pattern.match(value):
            raise ValueError("Argument 'value' does not match pattern '{}': '{}'".format(regex_pattern.pattern, value))
