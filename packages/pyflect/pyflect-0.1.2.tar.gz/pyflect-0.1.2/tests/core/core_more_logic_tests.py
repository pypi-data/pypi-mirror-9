from nose.tools import *
from pyflect import Reflected, Clonable

__author__ = 'bagrat'


class ModelObject(Clonable):
    def __init__(self, tag, base_class=None, *init_args):
        super(ModelObject, self).__init__(base_class, *init_args)

        self.tag = tag


class User(ModelObject):
    def __init__(self, tag, name):
        super(User, self).__init__(tag, User, tag, name)

        self.name = name


class UserORM(User):
    def __init__(self, tag, name, orm_field):
        super(UserORM, self).__init__(tag, name)

        self.orm_field = orm_field


def test_reflect_clone():
    user = User('tag', 'Bagrat')
    user_orm = UserORM('tag ORM', 'Bagrat ORM', 'ORM Field')

    model_fields = set(user.get_fields())
    orm_clone_fields = set(user_orm.clone().get_fields())

    assert len(model_fields.symmetric_difference(orm_clone_fields)) == 0
