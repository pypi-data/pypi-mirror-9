__author__ = 'bagrat'

from nose.tools import *
from pyflect.core.filter.impl import *


class SimpleAttrFilter(AttrFilter):
    to_be_removed = ['one', 'two', 'three']

    def __init__(self):
        AttrFilter.__init__(self)

    def _filter(self, field_list):
        return [f for f in field_list if f not in SimpleAttrFilter.to_be_removed]


def test_field_filter():
    sample_list = ['one', '2', 'three', '4', 'five']
    expected_list = ['2', '4', 'five']

    sff = SimpleAttrFilter()

    result = sff(sample_list)

    assert len(expected_list) == len(result)

    for e in expected_list:
        assert e in result


def test_field_filter_inverse():
    sample_list = ['one', '2', 'three', '4', 'five']
    expected_list = ['one', 'three']

    sff = SimpleAttrFilter()

    result = sff.inverse(sample_list)

    assert len(expected_list) == len(result)

    for e in expected_list:
        assert e in result


def test_list_field_filter():
    sample_list = ['one', '2', 'three', '4', 'five', 'zix']
    exclude_list = ['2', '4']
    expected_list = ['one', 'three', 'five']

    lff = ListAttrFilter(exclude_list, 'zix')

    result = lff(sample_list)

    assert len(expected_list) == len(result)

    for e in expected_list:
        assert e in result


def test_prefix_field_filter():
    sample_list = ['a_1', 'a_2', '3', '4', '5', 'a_6', '7', 'a8', 'a_']
    prefix = 'a_'
    expected_list = ['3', '4', '5', '7', 'a8']

    pff = PrefixAttrFilter(prefix)

    result = pff(sample_list)

    assert len(result) == len(expected_list)
    for e in expected_list:
        assert e in result


def test_prefix_filter_non_string():
    sample_list = ['a_1', 'a_2', '3', '4', 0, 0, 0, '5', 'a_6', '7', 'a8', 'a_']
    prefix = 'a_'
    expected_list = ['3', '4', 0, 0, 0, '5', '7', 'a8']

    pff = PrefixAttrFilter(prefix)

    result = pff(sample_list)

    assert len(result) == len(expected_list)
    for e in expected_list:
        assert e in result


