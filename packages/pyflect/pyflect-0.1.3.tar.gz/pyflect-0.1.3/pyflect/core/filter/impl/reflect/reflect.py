from pyflect.core.filter import AttrFilter
from pyflect.core.filter.impl.basic import PrefixAttrFilter

__author__ = 'bagrat'


class PrivateAttrFilter(PrefixAttrFilter):
    """Private attribute name filter

    Filters strings that start with '_'
    """
    def __init__(self):
        PrefixAttrFilter.__init__(self, '_')


class StaticAttrFilter(AttrFilter):
    """Static attribute name filter

    Filters all fields that belong to the Class of the object
    """
    def __init__(self, clazz):
        AttrFilter.__init__(self)

        self._clazz = clazz

    def _filter(self, field_list):
        return [field for field in field_list if not hasattr(self._clazz, field)]
