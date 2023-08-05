import inspect

from pyflect.core.filter.impl import ListAttrFilter, PrefixAttrFilter, PrivateAttrFilter, StaticAttrFilter
from pyflect.ex import InitializationError, FilterError
from pyflect.util import hasmethod, iscallable

__author__ = 'bagrat'


class Reflected(object):
    """Reflection Base Class

    Provides reflection methods to dynamically get available attributes of an object, the Class of which
     inherits from this one.
    """

    def __init__(self):
        super(Reflected, self).__init__()

    def _filter_attrs(self, attrs, *attr_filters):
        """Filter list of attributes

        Filters a list of attributes according to provided AttrFilter instances.
        :param attrs: Attribute list to be filtered
        :param attr_filters: List of filters
        :return: List of attributes that passed the filtering
        """
        _attrs = attrs[:]
        _attr_filters = []

        if attr_filters is not None:
            _attr_filters = list(attr_filters)

        for af in _attr_filters:
            if not iscallable(af):
                raise FilterError('A field filter must be callable')
            elif len(inspect.getargspec(getattr(af, '__call__'))[0]) != 2:
                raise FilterError('A field filter must accept exactly one argument')
            _attrs = af(_attrs)

        return _attrs

    def _get_attrs(self, *attr_filters):
        """Get attributes with prior filtering

        :param attr_filters: List of filters
        :return: List of all attributes of the object that passed the filtering
        """
        all_attrs = dir(self)

        return self._filter_attrs(all_attrs, *attr_filters)

    def get_all_fields(self, *attr_filters):
        """Get all fields of the object with prior filtering

        :param attr_filters: List of filters
        :return: List of all fields of the object that passed the filtering
        """
        all_attr_names = self._get_attrs(*attr_filters)

        fields = []
        for attrName in all_attr_names:
            if not hasmethod(self, attrName):
                fields.append(attrName)

        return fields

    def get_all_methods(self, *attr_filters):
        """Get all methods of the object with prior filtering

        :param attr_filters: List of filters
        :return: List of all methods of the object that passed the filtering
        """
        all_attr_names = self._get_attrs(*attr_filters)
        all_fields = self.get_all_fields()

        return ListAttrFilter(all_fields).outof(all_attr_names)

    def get_fields(self, *attr_filters):
        """Get all public fields of the object with prior filtering

        :param attr_filters: List of filters
        :return: List of all public fields of the object that passed the filtering
        """
        return PrivateAttrFilter().outof(self.get_all_fields(*attr_filters))

    def get_methods(self, *attr_filters):
        """Get all public methods of the object with prior filtering

        :param attr_filters: List of filters
        :return: List of all public methods of the object that passed the filtering
        """
        return PrivateAttrFilter().outof(self.get_all_methods(*attr_filters))
