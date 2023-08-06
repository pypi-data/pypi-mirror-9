import importlib
import inspect
import types
import collections

from rambutan3 import RArgs
from rambutan3.type.matcher.RAbstractTypeMatcher import RAbstractTypeMatcher
from rambutan3.type.matcher.annotation.NONE import NONE
from rambutan3.type.matcher.error.RCheckArgsError import RCheckArgsError
from rambutan3.type.matcher.RInstanceMatcher import RInstanceMatcher
from rambutan3.type.matcher.cls_or_self.RClassInstanceMatcher import RClassInstanceMatcher
from rambutan3.type.matcher.cls_or_self.RSelfInstanceMatcher import RSelfInstanceMatcher
from rambutan3.type.matcher.error.RCheckArgsErrorFormatterWithPrefix import RCheckArgsErrorFormatterWithPrefix


ParamTuple = collections.namedtuple('ParamTuple', ['param', 'value_matcher'])

# TODO: Disable non-RAbstractTypeMatcher annotations?  Me thinks yes.
class _RCheckArgs:
    """Special internal class used by @check_args"""

    __FUNC_TYPE_TUPLE = (types.FunctionType, staticmethod, classmethod)
    __ERROR_FORMATTER = RCheckArgsErrorFormatterWithPrefix()

    def __init__(self, func: (types.FunctionType, staticmethod, classmethod)):
        RArgs.check_is_instance(func, self.__FUNC_TYPE_TUPLE, "func")
        if isinstance(func, (staticmethod, classmethod)):
            self.__unwrapped_func = getattr(func, '__func__')
        else:
            self.__unwrapped_func = func
        self.__func_signature = inspect.signature(self.__unwrapped_func)
        #: :type: dict of (str, Parameter)
        name_to_param_dict = self.__func_signature.parameters
        #: :type: list of ParamTuple
        self.__param_tuple_list = []
        #: :type index: int
        #: :type param: Parameter
        for index, param in enumerate(name_to_param_dict.values()):
            # Check param annotation
            if param.annotation is inspect.Parameter.empty:
                raise RCheckArgsError("Missing type annotation for parameter #{}: '{}'".format(1 + index, param.name))
            # elif isinstance(param.annotation, type):
            #     value_matcher = INSTANCE_OF(param.annotation)
            elif isinstance(param.annotation, RAbstractTypeMatcher):
                value_matcher = param.annotation
            else:
                raise RCheckArgsError("Parameter #{} '{}' annotation: Expected type '{}', but found type '{}'"
                                      .format(1 + index,
                                              param.name,
                                              RAbstractTypeMatcher.__name__,
                                              type(param.annotation).__name__))

            # Check param default value
            if param.default is not inspect.Parameter.empty:
                value_matcher.check(param.default, self.__ERROR_FORMATTER,
                                    "Default value for argument #{} '{}': ", 1 + index, param.name)

            param_tuple = ParamTuple(param=param, value_matcher=value_matcher)
            self.__param_tuple_list.append(param_tuple)

        # TODO: Why is return_annotation checking disabled?
        if self.__func_signature.return_annotation is inspect.Signature.empty:
            self.__return_value_matcher = NONE
        # elif isinstance(self.__func_signature.return_annotation, type):
        #     self.__return_value_matcher = INSTANCE_OF(self.__func_signature.return_annotation)
        elif isinstance(self.__func_signature.return_annotation, RAbstractTypeMatcher):
            self.__return_value_matcher = self.__func_signature.return_annotation
        else:
            raise RCheckArgsError("Return value annotation: Expected type '{}', but found type '{}'"
                                  .format(RAbstractTypeMatcher.__name__,
                                          type(self.__func_signature.return_annotation).__name__))
        self.__func = func

    def __call__(self, *args, **kwargs):
        try:
            bound_args = self.__func_signature.bind(*args, **kwargs)
        except TypeError as e:
            msg = "Failed to bind arguments: {}: {}".format(type(e).__name__, e)
            raise RCheckArgsError(msg) from e

        arg_num_offset = 1
        for param_index, param_tuple in enumerate(self.__param_tuple_list):
            if isinstance(param_tuple.value_matcher, (RSelfInstanceMatcher, RClassInstanceMatcher)):
                # The first parameter for a method is always 'self', but when calling a method, 'self' is passed implicitly.
                # The first parameter for a classmethod is always 'cls', but when calling a method, 'cls' is passed implicitly.
                # Reduce the offset by one as first arg for method or classmethod will not be 'self' or 'cls'.
                arg_num_offset -= 1
                if 0 != param_index:
                    raise RCheckArgsError("SELF() and CLS() are only valid for first argument")
                if isinstance(param_tuple.value_matcher, RClassInstanceMatcher):
                    if not isinstance(self.__func, classmethod):
                        raise RCheckArgsError("CLS() is only valid for class methods (functions using @classmethod decorator)")
                    # The first argument ('cls') is never available here.  Continue with faith...
                    continue

            if param_tuple.param.name in bound_args.arguments:
                value = bound_args.arguments[param_tuple.param.name]
            elif param_tuple.param.default is not inspect.Parameter.empty:
                value = param_tuple.param.default
            else:
                # It may be impossible to hit this branch due to bind() call above.
                raise RCheckArgsError("Argument #{} ({}) is missing and has no default value"
                                      .format(param_index + arg_num_offset, param_tuple.param.name))

            if inspect.Parameter.VAR_POSITIONAL == param_tuple.param.kind:
                value_tuple = value
                for value_index, value in enumerate(value_tuple):
                    param_tuple.value_matcher.check(value, self.__ERROR_FORMATTER, "*{}[{}]: ",
                                                    param_tuple.param.name, value_index)
            elif inspect.Parameter.VAR_KEYWORD == param_tuple.param.kind:
                key_value_dict = value
                for key, value in key_value_dict.items():
                    param_tuple.value_matcher.check(value, self.__ERROR_FORMATTER, "**{}['{}']: ",
                                                    param_tuple.param.name, key)
            else:
                param_tuple.value_matcher.check(value, self.__ERROR_FORMATTER, "Argument #{} '{}': ",
                                                param_index + arg_num_offset, param_tuple.param.name)

        result = self.__unwrapped_func(*args, **kwargs)

        # TODO: Why is return_annotation checking disabled?
        self.__return_value_matcher.check(result, self.__ERROR_FORMATTER, "Return value: ")

        return result

    # def _get_cls(self):
    #     # Python does not allow this code to run from __init__, so do it here.
    #     if not hasattr(self, '__cls'):
    #         module_name = self.__unwrapped_func.__module__
    #         module = importlib.import_module(module_name)
    #         # Ex: 'MyClass.my_classmethod'
    #         qual_name = self.__unwrapped_func.__qualname__
    #         name_list = qual_name.split('.')
    #
    #         # We need a for loop to handle nested classes, e.g., 'MyClass.MyNestedClass.my_classmethod'
    #         cls = module
    #         # Skip last item (method name)
    #         for name in name_list[:-1]:
    #             cls = getattr(cls, name)
    #
    #         self.__cls = cls
    #
    #     return self.__cls


def check_args(func: (types.FunctionType, staticmethod, classmethod)) -> types.FunctionType:
    """Function decorator for all types of functions:
    * Regular functions
    * Regular methods in classes
    * Class methods in classes (decorated with @classmethod)
    * Static methods in classes (decorated with @staticmethod)

    Each time the function is called, arguments are matched against parameter annotations.
    Mismatches are rejected and reported at runtime.

    Example function:
    <pre>{@code
    @check_args
    def add(x: INT, y: INT) -> INT:
        return x + y
    }</pre>

    Example function:
    <pre>{@code
    @check_args
    def foreach(data: NON_EMPTY_LIST, func: FUNC_OF(ANY).returnsNothing()):
        for x in data:
            func(x)
    }</pre>

    Optionally, for the above function, the return type matcher {@link NONE} may be used.  Surprisingly, all void Python
    functions return special singleton value {@code None} if, either, (a) no return statement exists, or (b) an empty
    return statement is used.  Some programming languages make the distinction between functions (with return types) and
    procedures (without return types).

    Example function with {@code NONE} return type matcher:
    <pre>{@code
    @check_args
    def foreach(data: NON_EMPTY_LIST, func: FUNC_OF(ANY).returnsNothing()) -> NONE:
        for x in data:
            func(x)
    }</pre>

    Example classmethod: (Order of @check_args and @classmethod is important!)
    <pre>{@code
    @check_args
    @classmethod
    def get_data(cls: CLS()) -> NON_EMPTY_TUPLE_OF(INT):
        return (1,2,3)
    }</pre>

    Example staticmethod: (Order of @check_args and @staticmethod is important!)
    <pre>{@code
    @check_args
    @staticmethod
    def get_data() -> NON_EMPTY_TUPLE_OF(INT):
        return (1,2,3)
    }</pre>

    Example staticmethod: (Order of @check_args and @staticmethod is important!)
    <pre>{@code
    @check_args
    @staticmethod
    def add(x: NON_NEGATIVE_NUMBER, y: NON_NEGATIVE_NUMBER) -> NON_NEGATIVE_NUMBER:
        return x + y
    }</pre>
    """
    wrapped_func = _RCheckArgs(func)

    if isinstance(func, classmethod):
        @classmethod
        def check_args_delegator(*args, **kwargs):
            x = wrapped_func(*args, **kwargs)
            return x
    elif isinstance(func, staticmethod):
        @staticmethod
        def check_args_delegator(*args, **kwargs):
            x = wrapped_func(*args, **kwargs)
            return x
    else:
        # Why this additional layer of indirection?
        # A pure function does not eat special argument 'self'.
        # A functor (class that implements __call__()) will eat special argument 'self'.
        def check_args_delegator(*args, **kwargs):
            x = wrapped_func(*args, **kwargs)
            return x

    check_args_delegator.__doc__ = func.__doc__
    return check_args_delegator


# @lru_cache(maxsize=None)
# def TYPE_MATCHER_OF(instance_matcher: RInstanceMatcher) -> RInstanceMatcherMatcher:
#     x = RInstanceMatcherMatcher(instance_matcher)
#     return x

# TODO: Move remaining items out

__TRACEBACK = RInstanceMatcher(types.TracebackType)

def TRACEBACK() -> RInstanceMatcher:
    return __TRACEBACK

__FRAME = RInstanceMatcher(types.FrameType)

def FRAME() -> RInstanceMatcher:
    return __FRAME

# __CAN_WRITE = RAttrMatcher(RTokenText("write"))
#
# def CAN_WRITE() -> RAttrMatcher:
#     return __CAN_WRITE
