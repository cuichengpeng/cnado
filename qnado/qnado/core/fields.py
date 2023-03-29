import sys
from abc import ABCMeta


class FieldMetaclass(ABCMeta):
    def __repr__(cls):
        return cls.__name__

    @property
    def swagger_dtype(cls):
        if cls.dtype == bool:
            dtype_str = 'boolean'
        elif cls.dtype == str:
            dtype_str = 'string'
        elif cls.dtype == int:
            dtype_str = 'integer'
        elif cls.dtype == dict:
            dtype_str = 'object'
        elif cls.dtype == list:
            dtype_str = 'array'
        elif cls.dtype == float:
            dtype_str = 'float'
        else:
            dtype_str = cls.dtype.__name__
        return dtype_str


class Field(metaclass=FieldMetaclass):
    pass


class BoolField(Field):
    dtype = bool


class StringField(Field):
    dtype = str


class FloatField(Field):
    dtype = float


class IntegerField(Field):
    dtype = int


class DictField(Field):
    dtype = dict


class ListField(Field):
    dtype = list


def get_field_class(field_str):
    return sys.modules[__name__].__dict__.get(field_str)
