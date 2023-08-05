import inspect


def get_argument_names(method):
    """
    Returns list of method's positional argument names without `self`.
    """
    argument_names = inspect.getargspec(method).args
    try:
        argument_names.remove("self")
    except ValueError:
        pass
    return argument_names


def get_methods(instance):
    """
    Extracts public methods of the given instance.
    Internal methods are discarded (ones starting with `_`).
    Returns list of pairs (method_name, method).
    """
    def is_public_method(method):
        return inspect.ismethod(method) and not method.__name__.startswith("_")
    methods = inspect.getmembers(instance, is_public_method)
    return methods


def get_method_signatures(instance):
    """
    Extracts public method signatures of the given instance,
    that is method name and arguments names.
    Returns list of pairs (method_name, argument_names).
    """
    method_names, methods = zip(*get_methods(instance))
    argument_names = map(get_argument_names, methods)
    method_signatures = zip(method_names, argument_names)
    return method_signatures
