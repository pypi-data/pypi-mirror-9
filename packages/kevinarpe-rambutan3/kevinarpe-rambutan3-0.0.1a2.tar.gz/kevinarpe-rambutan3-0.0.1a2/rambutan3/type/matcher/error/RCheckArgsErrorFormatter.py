"""Format exception messages for {@link RValueMatcher#check()}

@author Kevin Connor ARPE (kevinarpe@gmail.com)
"""

import inspect


# Trick to satisfy Python compiler about RValueMatcher being undefined without an import statement.
try:
    eval('RValueMatcher')
except:
    RValueMatcher = None


class RCheckArgsErrorFormatter:
    """Used by {@link RValueMatcher#check()} to format exception messages"""

    def format(self, matcher: RValueMatcher, value, *args, **kwargs) -> str:
        """Creates an exception message for a failed value matcher check

        @param matcher (RValueMatcher)
               value matcher associated with failed check
        @param value
               value associated with failed check
        @param *args
               unused, but exists for signature override compatibility
        @param **kwargs
               unused, but exists for signature override compatibility

        @return exception message
        """
        value_str = self.__str__(value)
        x = "Expected type '{}', but found value: {}".format(matcher, value_str)
        return x

    def __str__(self, value) -> str:
        """Converts any value to a string

        There is special handling for function pointers.

        @param value
               value associated with failed check

        @return value as string
        """
        value_str = str(value)
        if value is not None:
            if inspect.isfunction(value):
                value_str = str(inspect.signature(value))
            value_str = "{}='{}'".format(type(value).__name__, value_str)
        return value_str
