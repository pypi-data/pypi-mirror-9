import importlib
import inspect
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.error.RCheckArgsError import RCheckArgsError


RAbstractClassOrSelfInstanceMatcher = None
class RAbstractClassOrSelfInstanceMatcher(RAbstractTypeMatcher):

    def __init__(self):
        super().__init__()
        stack_list = inspect.stack()
        # 0, 1, 2, 3 -> to the correct stack frame
        # 0: This method
        # 1: Subclass ctor -- RSelfInstanceMatcher or RClassInstanceMatcher
        # 2: Annotation macro -- SELF() or CLS()
        # 3: Target module / class point of method declaration -- def xyz(self: SELF()[, ...])
        if len(stack_list) < 4:
            raise RCheckArgsError("Failed to find declaring class via stack")
        caller_tuple = stack_list[3]
        caller_frame = caller_tuple[0]
        caller_locals_dict = caller_frame.f_locals
        if '__module__' not in caller_locals_dict:
            raise RCheckArgsError("Failed to find special local variable '__module__': Perhaps this function is not defined within a class?")
        # Ex: rambutan.types.matcher.RSelfTypeChecker
        caller_module_name = caller_locals_dict['__module__']
        self.__caller_module = importlib.import_module(caller_module_name)
        # Ex: RSelfTypeChecker
        self.__caller_class_name = caller_locals_dict['__qualname__']

    @property
    def _caller_class(self):
        # Python does not allow this code to run from __init__, so do it here.
        if not hasattr(self, '__caller_class'):
            self.__caller_class = getattr(self.__caller_module, self.__caller_class_name)
        return self.__caller_class

    # @override
    def __eq__(self, other: RAbstractClassOrSelfInstanceMatcher) -> bool:
        if not isinstance(other, type(self)):
            return False
        x = (self._caller_class == other._caller_class)
        return x

    # @override
    def __hash__(self) -> int:
        x = hash((type(self), self._caller_class))
        return x
