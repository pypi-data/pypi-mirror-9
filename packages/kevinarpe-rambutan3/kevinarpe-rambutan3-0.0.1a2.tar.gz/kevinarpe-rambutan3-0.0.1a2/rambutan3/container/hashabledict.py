

# Ref: http://code.activestate.com/recipes/414283/
class hashabledict(dict):

    def __hash__(self):
        # x = hash(tuple(sorted(self.items())))
        # The hash function relies on sorting, but many data types (e.g. sets) do not sort consistently.
        # A more reliable alternative is:
        x = hash(frozenset(self.items()))
        return x
