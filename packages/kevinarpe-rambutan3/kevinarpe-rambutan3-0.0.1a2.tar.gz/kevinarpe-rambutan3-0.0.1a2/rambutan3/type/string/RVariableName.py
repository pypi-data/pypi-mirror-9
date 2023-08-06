import re
from rambutan3.type.string.RPatternText import RPatternText


class RVariableName(RPatternText):
    """
    Wraps a {@link str} value that is a valid C programming language variable:
    (1) Starts with [A-Za-z_]
    (2) Followed by zero or more [0-9A-Za-z_]

    Examples: email_address, telephone_number123, or __something_very_private

    This class is fully tested.

    @author Kevin Connor ARPE (kevinarpe@gmail.com)
    """

    __TOKEN_PATTERN = re.compile(r"^[A-Za-z_][0-9A-Za-z_]*$")

    def __init__(self, value: str):
        super().__init__(value=value, regex_pattern=RVariableName.__TOKEN_PATTERN)
