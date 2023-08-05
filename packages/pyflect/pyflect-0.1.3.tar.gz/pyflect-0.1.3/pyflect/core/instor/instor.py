"""
Module for dynamically finding modules and classes as well as creating instances dynamically
"""
import importlib
import inspect

__author__ = 'bagrat'


def get_class(clazz, module=None):
    """Get class by its name

    If the module is not specified, the class name should be either the absolute path of the class, or it should be
     imported into the callers module (using from ... import clazz)

    :param clazz: The name of the class to be returned
    :param module: Optional module to look the specified class in
    :return: Class corresponding to the given name
    """

    parts = clazz.split('.')
    start_i = 1

    if len(parts) > 1:
        module = ".".join(parts[:-1])
        m = importlib.import_module(module)
    else:
        m = module if module else _get_caller_module(1)
        start_i = 0
    for comp in parts[start_i:]:
        m = getattr(m, comp)
    return m


def new(clazz, *args, **kwargs):
    """Create a new instance of class 'clazz'

    :param clazz: Class name to create a new instance of
    :param args: Positional arguments to be passed to the constructor of the class
    :param kwargs: Keyword arguments to be passed to the constructor of the class
    :return: The created instance
    """

    return get_class(clazz, _get_caller_module(1))(*args, **kwargs)


def _get_caller_module(depth=0):
    """Get the module from where this method was called

    If this method is wrapped into another one, and the client is calling the wrapper method, this will return the
     wrapper method. The solution to this situation is to specify the depth when calling this method. For this example
     it should be 1.

    :param depth: The depth of the call
    :return: The module instance
    """

    f = inspect.stack()[1 + depth]
    return inspect.getmodule(f[0])