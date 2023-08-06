from rambutan3.type.string.RStringDelegator import RStringDelegator


def auto_quote(value):
    x = str(value)
    if isinstance(value, (str, RStringDelegator)):
        x = "'" + x + "'"
    return x
