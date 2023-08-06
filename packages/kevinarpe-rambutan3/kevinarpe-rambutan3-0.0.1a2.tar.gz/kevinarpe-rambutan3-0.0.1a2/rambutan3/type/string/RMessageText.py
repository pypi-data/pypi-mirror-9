from rambutan3.type.string.RNonEmptyStr import RNonEmptyStr


class RMessageText(RNonEmptyStr):
    """
    Wraps a {@link str} value that is not empty (length > 0) and has at least one non-whitespace character.

    This class is used to represent strings used for human-readable messages.  Empty strings and strings with only
    whitespace will not be a useful message.

    This class is fully tested.

    @author Kevin Connor ARPE (kevinarpe@gmail.com)
    """

    def __init__(self, value: str):
        """
        @param value
               any non-empty string with at least one non-whitespace character, e.g., {@code "Hello"}.
               Otherwise, any amount of whitespace is allowed.

        @throws TypeError
                if {@code value} is not type {@link str}
        @throws ValueError
                if {@code value} has length zero or all whitespace characters

        @see str#isspace()
        """
        super().__init__(value)
        if value.isspace():
            raise ValueError("Argument 'value' is only whitespace: '{}'".format(value))
