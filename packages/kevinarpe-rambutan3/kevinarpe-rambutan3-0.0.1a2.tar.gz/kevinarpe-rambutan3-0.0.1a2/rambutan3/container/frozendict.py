

# Ref: http://code.activestate.com/recipes/414283/
# Ref: http://legacy.python.org/dev/peps/pep-0416/
class frozendict(dict):

    @property
    def _blocked_attribute(obj):
        raise AttributeError("A frozendict cannot be modified.")

    # _blocked_attribute = property(_blocked_attribute)

    __delitem__ = __setitem__ = clear = _blocked_attribute
    pop = popitem = setdefault = update = _blocked_attribute

    def __new__(cls, *args, **kwargs):
        new = dict.__new__(cls)
        dict.__init__(new, *args, **kwargs)
        return new

    def __init__(self, *args, **kwargs):
        pass

    def __hash__(self):
        try:
            return self._cached_hash
        except AttributeError:
            # h = self._cached_hash = hash(tuple(sorted(self.items())))
            # The hash function relies on sorting, but many data types (e.g. sets) do not sort consistently.
            # A more reliable alternative is:
            h = self._cached_hash = hash(frozenset(self.items()))
            return h

    def __repr__(self):
        x = dict.__repr__(self)
        y = "frozendict({})".format(x)
        return y
