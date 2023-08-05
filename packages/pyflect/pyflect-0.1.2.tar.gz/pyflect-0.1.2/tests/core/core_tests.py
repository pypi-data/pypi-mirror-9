__author__ = 'bagrat'

from nose.tools import *
from pyflect.core import Reflected, Clonable


class RefObj(Reflected):
    class_field = 'classField'

    def __init__(self):
        Reflected.__init__(self)

        self.inst_field = 0

    def new_method(self):
        pass

    def _private_method(self):
        pass

    @staticmethod
    def static_method():
        pass

    @classmethod
    def class_method(cls):
        pass


def assert_all_fields(expected, actual):
    exp = set(expected).union(['__module__', '__dict__', '__weakref__'])
    act = set(actual) - set(dir(object()))

    return len(exp.difference(act)) == 0


def assert_all_methods(expected, actual):
    exp = set(expected)
    act = set(actual) - set(dir(object()))

    return len(exp - act) == 0


def test_base_ref_obj():
    ro = RefObj()

    expected_fields = ['class_field', 'inst_field']
    expected_all_fields = [] + expected_fields
    expected_methods = ['get_all_fields', 'get_all_methods', 'get_fields', 'get_methods',
                        'new_method', 'static_method', 'class_method']
    expected_all_methods = ['_private_method', '_filter_attrs', '_get_attrs'] + expected_methods

    all_fields = ro.get_all_fields()
    fields = ro.get_fields()
    all_methods = ro.get_all_methods()
    methods = ro.get_methods()

    assert assert_all_fields(expected_all_fields, all_fields)
    assert len(set(expected_fields).symmetric_difference(fields)) == 0
    assert assert_all_methods(expected_all_methods, all_methods)
    assert len(set(expected_methods).symmetric_difference(methods)) == 0


class SomeModel(Clonable):
    field_val = 123

    def __init__(self, base_class=None):
        super(SomeModel, self).__init__(base_class)

        self.f1 = SomeModel.field_val
        self.f2 = None


class A(Clonable):
    def __init__(self):
        super(A, self).__init__(A)

        self.a = 1
        self.b = 2
        self.c = 3


class B(A):
    def __init__(self):
        super(B, self).__init__()

        self.d = 4
        self.e = 5


def test_bro_clone():
    sm = SomeModel()

    exp_val = 2
    sm.f2 = exp_val

    sm2 = sm.clone()

    assert sm2.f1 == SomeModel.field_val
    assert sm2.f2 == exp_val


def test_bro_inherit_stop():
    inst1 = B()

    inst2 = inst1.clone()

    assert inst1.a == inst2.a
    assert inst1.b == inst2.b
    assert inst1.c == inst2.c
    assert not hasattr(inst2, 'd')
    assert not hasattr(inst2, 'e')


class A2(Clonable):
    def __init__(self, a, b):
        super(A2, self).__init__(A2, a, b)

        self.a = a
        self.b = b
        self.c = 3


class B2(A2):
    init_param_a = 123
    init_param_b = 456

    def __init__(self):
        super(B2, self).__init__(B2.init_param_a, B2.init_param_b)

        self.d = 4
        self.e = 5


def test_bro_inherit_stop_with_init_args():
    inst1 = B2()

    inst2 = inst1.clone()

    assert inst1.a == B2.init_param_a
    assert inst1.b == B2.init_param_b
    assert inst1.c == inst2.c
    assert not hasattr(inst2, 'd')
    assert not hasattr(inst2, 'e')