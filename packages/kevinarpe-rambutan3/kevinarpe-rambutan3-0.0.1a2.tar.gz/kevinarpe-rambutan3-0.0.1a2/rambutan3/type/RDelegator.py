

class RDelegator:
    """
    Delegates, absolutely.
    This maybe surprising when using issubclass(), as self.__getattribute__("__class__") is also delegated!

    @author Kevin Connor ARPE (kevinarpe@gmail.com)
    """

    def __init__(self, delegate):
        super().__setattr__("__delegate", delegate)

    def _super_getattribute(self, name):
        """
        Provides special non-delegated access to {@code object#__getattribute__()}.
        """
        x = super().__getattribute__(name)
        return x

    def __getattr__(self, name):
        delegate = super().__getattribute__("__delegate")
        return delegate.__getattr__(name)

    def __str__(self):
        delegate = super().__getattribute__("__delegate")
        return delegate.__str__()

    def __sizeof__(self):
        delegate = super().__getattribute__("__delegate")
        return delegate.__sizeof__()

    def __setattr__(self, name, value):
        delegate = super().__getattribute__("__delegate")
        return delegate.__setattr__(name, value)

    def __repr__(self):
        delegate = super().__getattribute__("__delegate")
        return delegate.__repr__()

    def __reduce_ex__(self, protocol_version):
        delegate = super().__getattribute__("__delegate")
        return delegate.__reduce_ex__(protocol_version)

    def __reduce__(self):
        delegate = super().__getattribute__("__delegate")
        return delegate.__reduce__()

    def __ne__(self, other):
        delegate = super().__getattribute__("__delegate")
        return delegate.__ne__(other)

    def __lt__(self, other):
        delegate = super().__getattribute__("__delegate")
        return delegate.__lt__(other)

    def __le__(self, other):
        delegate = super().__getattribute__("__delegate")
        return delegate.__le__(other)

    def __hash__(self):
        delegate = super().__getattribute__("__delegate")
        return delegate.__hash__()

    def __gt__(self, other):
        delegate = super().__getattribute__("__delegate")
        return delegate.__gt__(other)

    # def __getattribute__(self, name):
    #     delegate = super().__getattribute__("__delegate")
    #     return delegate.__getattribute__(name)

    def __ge__(self, other):
        delegate = super().__getattribute__("__delegate")
        return delegate.__ge__(other)

    def __format__(self, *args, **kwargs):
        delegate = super().__getattribute__("__delegate")
        return delegate.__format__(*args, **kwargs)

    def __eq__(self, other):
        delegate = super().__getattribute__("__delegate")
        return delegate.__eq__(other)

    def __dir__(self):
        delegate = super().__getattribute__("__delegate")
        return delegate.__dir__()

    def __delattr__(self, name):
        delegate = super().__getattribute__("__delegate")
        return delegate.__delattr__(name)
