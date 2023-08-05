"""
This module defines classes for filtering lists of objects which are used to filter class fields names for various
operations.
"""
from pyflect.util import hasmethod

__author__ = 'bagrat'


class AttrFilter():
    """Base class for a filter

    This is a callable class, that takes a list of objects and filters them according to a specific rule. The filtering
     should be defined as a factory method, by inheriting from this class and implementing the _filter method.

    The resulting class is a callable class and the instances can be used like functions.
    """

    def __init__(self):
        pass

    def _filter(self, field_list):
        """Filter the provided list

        This method should be implemented by subclasses and the implementation itself will define the filtering.

        :param field_list: The initial list of objects
        :return: The filtered list of objects
        """
        pass  # pragma: no cover

    def __call__(self, field_list):
        return self._filter(field_list)

    def inverse(self, field_list):
        """Inverse filtering

        This method performs the inverse filtering of the list, i.e. leaves only the objects that would be filtered in
         the regular call.

        :param field_list:
        :return:
        """
        result = self._filter(field_list)
        return [field for field in field_list if field not in result]

    def outof(self, field_list):
        return self(field_list)
