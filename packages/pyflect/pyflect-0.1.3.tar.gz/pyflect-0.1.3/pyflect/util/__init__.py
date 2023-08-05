import inspect

__author__ = 'bagrat'


def ismethod(obj):
    """Wrapper. See https://docs.python.org/2/library/inspect.html#inspect.isroutine

    :param obj:
    :return:
    """
    return inspect.isroutine(obj)


def iscallable(obj):
    """Check if the obj is a raw callable

    :param obj: The object to be checked
    :return: boolean
    """
    return hasattr(obj, '__call__')


def hasmethod(obj, name):
    """Check if the obj has the specified method

    :param obj: The object to be checked
    :param name: The name of the method to be looked up
    :return: boolean
    """
    return hasattr(obj, name) and ismethod(getattr(obj, name))


def isiterable(obj):
    """Check if the obj is a iterable

    :param obj: The object to be checked
    :return: boolean
    """
    return hasattr(obj, '__iter__')