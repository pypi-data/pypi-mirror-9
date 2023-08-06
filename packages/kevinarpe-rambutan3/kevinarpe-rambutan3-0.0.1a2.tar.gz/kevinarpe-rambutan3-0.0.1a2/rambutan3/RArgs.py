"""Simple argument checking functions

This module is fully tested.

@author Kevin Connor ARPE (kevinarpe@gmail.com)
"""


def check_not_none(value, arg_name: str):
    """Tests if a value is not none.

    @param value
           reference to test
    @param arg_name (str)
           name of argument to be used in thrown exception message, e.g., {@code "max_size"}

    @return checked value

    @throws ValueError
            if {@code value} is {@code None}
    """
    if value is None:
        raise ValueError("Argument '{}' is None".format(arg_name))
    return value


def check_iterable_items_not_none(iterable, arg_name: str):
    """Tests if an iterable and all items are not {@code None}.

    An empty iterable will pass this test.

    @param iterable
           reference to test
    @param arg_name (str)
           name of argument to be used in thrown exception message, e.g., {@code "file_name_list"}

    @return checked value

    @throws ValueError
            if {@code iterable} is {@code None} or any item is {@code None}

    @see #check_not_none()
    @see #check_iterable_not_empty()
    """
    check_not_none(iterable, arg_name)

    for index, value in enumerate(iterable):
        if value is None:
            raise ValueError("Iterable argument '{}[{}]' is None".format(arg_name, index))
    return iterable


__SENTINEL = object()


def check_iterable_not_empty(iterable, arg_name: str):
    """Tests if an iterable is not {@code None} and not empty

    @param iterable
           reference to test
    @param arg_name (str)
           name of argument to be used in thrown exception message, e.g., {@code "file_name_list"}

    @return checked value

    @throws ValueError
            if {@code iterable} is {@code None} or empty

    @see #check_not_none()
    @see #check_iterable_items_not_none()
    """
    check_not_none(iterable, arg_name)

    # Ref: http://stackoverflow.com/a/3114573/257299
    if __SENTINEL == next(iter(iterable), __SENTINEL):
        raise ValueError("Iterable argument '{}' is empty".format(arg_name))
    return iterable


def check_iterable_not_empty_and_items_not_none(iterable, arg_name: str):
    """Tests if an iterable is not {@code None}, not empty, and all items are not {@code None}.

    @param iterable
           reference to test
    @param arg_name (str)
           name of argument to be used in thrown exception message, e.g., {@code "file_name_list"}

    @return checked value

    @throws ValueError
            if {@code iterable} is {@code None}, empty, or any item is {@code None}

    @see #check_not_none()
    @see #check_iterable_not_empty()
    @see #check_iterable_items_not_none()
    """
    check_iterable_not_empty(iterable, arg_name)
    check_iterable_items_not_none(iterable, arg_name)
    return iterable


def check_is_instance(value, class_or_type_or_tuple_of: (type, tuple), arg_name: str, *arg_name_format_args):
    """Tests if a value is an instance of a type.

    Example: String value {@code "abc"} has type {@link str}.

    A value of {@code None} will pass this test if {@code class_or_type_or_tuple_of} is {@code type(None)}.

    @param value
           reference to test
    @param class_or_type_or_tuple_of
           class, type, or tuple of classes or types.  Must not be a list (or sequence).
    @param arg_name (str)
           name of argument to be used in thrown exception message, e.g., "file_name_list".
           May also be a {@link str#format()} string if arg_name is composed.
           Example: {@code "Index {}"}
    @param *arg_name_format_args
           zero or more arguments passed to {@link str#format()} along with {@code arg_name}
           Example: if {@code arg_name} is {@code "Index {}"}, then {@code *arg_name_format_args} might be {@code 7}.

    @return checked value

    @throws ValueError
            if {@code class_or_type_or_tuple_of} is {@code None}
    @throws TypeError
            if {@code value} has unexpected type, e.g., "abc" for int, or 123 for str

    @see #isinstance()
    @see str#format()
    @see #check_not_none()
    """
    # We don't need to check if 'value' is None here.  Built-in function 'isinstance' will work with None.
    check_not_none(class_or_type_or_tuple_of, "class_or_type_or_tuple_of")

    if not isinstance(value, class_or_type_or_tuple_of):
        formatted_arg_name = arg_name.format(*arg_name_format_args)
        if isinstance(class_or_type_or_tuple_of, tuple):
            x = "'" + "', '".join([type_.__name__ for type_ in class_or_type_or_tuple_of]) + "'"
            raise TypeError("Argument '{}': Expected any type of {}, but found '{}': '{}'"
                            .format(formatted_arg_name, x, type(value).__name__, value))
        else:
            raise TypeError("Argument '{}': Expected type '{}', but found '{}': '{}'"
                            .format(formatted_arg_name, class_or_type_or_tuple_of.__name__, type(value).__name__, value))
    return value


def check_is_subclass(subclass: type, superclass: type, subclass_arg_name: str):
    """Tests if a type is a subclass of another type.

    If {@code subclass} and {@code superclass} are the same, this test will pass.

    @param subclass (type)
           type to test
    @param superclass (type)
           expected (super) type
    @param subclass_arg_name (str)
           name of argument to be used in thrown exception message, e.g., "file_handle_type".

    @return checked subclass type

    @see #issubclass()
    """
    check_not_none(subclass, "subclass")
    check_not_none(superclass, "superclass")

    if not issubclass(subclass, superclass):
        raise TypeError("Argument '{}': Expected subclass of type '{}', but found type '{}'"
                        .format(subclass_arg_name, superclass.__name__, subclass.__name__))
    return subclass


# def check_is_any_subclass(subclass, superclass_iterable, subclass_arg_name: str):
#     check_not_none(subclass, "subclass")
#     check_iterable_not_empty_and_items_not_none(superclass_iterable, "superclass_iterable")
#
#     for superclass in superclass_iterable:
#         if issubclass(subclass, superclass):
#             return subclass
#
#     x = "'" + "', '".join(superclass_iterable) + "'"
#     raise TypeError("Argument '{}': Expected any subclass of type '{}', but found type '{}'"
#                     .format(subclass_arg_name, x, subclass))
