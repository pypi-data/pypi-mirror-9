from pyflect.core.filter import AttrFilter
from pyflect.util import hasmethod, isiterable

__author__ = 'bagrat'


class ListAttrFilter(AttrFilter):
    """List excluding filter

    This filter excludes a specified list from the provided one.
    """

    def __init__(self, *args):
        AttrFilter.__init__(self)
        self._exclusions = []

        for arg in args:
            if isiterable(arg):
                self._exclusions += arg[:]
            else:
                self._exclusions.append(arg)

    def _filter(self, field_list):
        return [field for field in field_list if field not in self._exclusions]


class PrefixAttrFilter(AttrFilter):
    """Prefix bases filter

    This filter operates on objects that implement `startswith` method and removes ones that start with a specified
     prefix.
    """

    def __init__(self, prefix):
        AttrFilter.__init__(self)
        self._prefix = prefix

    def _filter(self, field_list):
        return [field for field in field_list if not (hasmethod(field, 'startswith') and
                                                      field.startswith(self._prefix))]

