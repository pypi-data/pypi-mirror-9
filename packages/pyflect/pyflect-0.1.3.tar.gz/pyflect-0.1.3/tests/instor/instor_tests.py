__author__ = 'bagrat'

from nose.tools import *
from pyflect.core.instor import *

from datetime import datetime


def test_get_class():
    d = get_class('datetime.datetime')

    import datetime

    assert d is datetime.datetime


class C:
    def __init__(self):
        pass


def test_new():
    c = new('C')

    assert isinstance(c, C)


def test_new_imported():
    year = 1991
    month = 12
    day = 10

    d = new('datetime', year, day=day, month=month)

    assert isinstance(d, datetime)
    assert d.year == year
    assert d.month == month
    assert d.day == day


@raises(AttributeError)
def test_new_ex():
    c = new('somethingreckless')
