import inspect
from pyflect.core.reflected import Reflected
from pyflect.core.filter.impl import ListAttrFilter, PrefixAttrFilter, StaticAttrFilter, PrivateAttrFilter
from pyflect.ex import FilterError
from pyflect.util import iscallable

__author__ = 'bagrat'


class Clonable(Reflected):
    """Provides an object with functionality to clone its field values

    """

    _pyflect_default_ex = None

    def __init__(self, base_class=None, *init_args):
        """

        Optionally, inheriting class may specify a stop point in terms of a class. For instance, if class A inherits
         Clonable by passing A as base_class parameter and class B inherits class A, then the clone functions called
         on an instance of class B will return an instance of class A with only its fields copied. Further let's call
         the stopping class a 'clone-inheritance stop class' - CIS class.

        :param base_class: The CIS class (as defined above). If not defined, the leave-child class in the inheritance
                            tree is picked
        :param init_args: Initial arguments to be passed to the CIS class constructor
        :return:
        """

        super(Clonable, self).__init__()

        self._pyflect_init_args = init_args  # TODO: add check for base_class args count

        if base_class is None:
            self._pyflect_base_class = self.__class__
        else:
            self._pyflect_base_class = base_class
        pass

    @classmethod
    def _default_field_filters(cls):
        """Default filters, that leave out Clonable-specific fields

        :return: List of AttrFilter instances
        """
        if cls._pyflect_default_ex is None:
            cls._pyflect_default_ex = []
            cls._pyflect_default_ex.append(ListAttrFilter('__weakref__', '__dict__', '__module__', '__doc__'))
            cls._pyflect_default_ex.append(PrefixAttrFilter('_pyflect'))
            cls._pyflect_default_ex.append(StaticAttrFilter(cls))

        return cls._pyflect_default_ex

    def _copy_field_value(self, field, to):
        """Copy the value of a filed to another object

        :param field: The field value to be copied
        :param to: The object where the value should be copied
        :return:
        """
        setattr(to, field, getattr(self, field))

    def _pyflect_clone_fields(self, fields, *field_filters):
        """Generic clone functionality

        First filters the provided list with the provided filters and then creates a new instance of either the same
         class or the CIS class with the initial parameters (if specified). Then just copies the filed values.

        :param fields:
        :param field_filters:
        :return:
        """
        _fields = self._filter_attrs(fields, *(tuple(self._default_field_filters()) + field_filters))

        c = self._pyflect_base_class(*self._pyflect_init_args)

        for field in _fields:
            if hasattr(c, field):
                self._copy_field_value(field, c)

        return c

    def clone_all(self, *field_filters):
        """Clone all fields with prior filtering

        :param field_filters: List of filters
        :return:
        """
        return self._pyflect_clone_fields(self.get_all_fields(), *field_filters)

    def clone(self, *field_filters):
        """Clone all public fields with prior filtering

        :param field_filters: List of filters
        :return:
        """
        return self.clone_all(PrivateAttrFilter(), *field_filters)


