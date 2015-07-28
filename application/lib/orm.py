__author__ = 'newbie'

from sqlalchemy.types import SmallInteger, TypeDecorator
from sqlalchemy.ext.mutable import Mutable


class MutableList(Mutable, list):
    def append(self, value):
        list.append(self, value)
        self.changed()

    @classmethod
    def coerce(cls, key, value):
        if not isinstance(value, MutableList):
            if isinstance(value, list):
                return MutableList(value)
            return Mutable.coerce(key, value)
        else:
            return value


class EnumInt(TypeDecorator):

    impl = SmallInteger

    def __init__(self, enum, *args, **kwargs):
        self._enum = enum
        super().__init__(*args, **kwargs)

    def process_bind_param(self, enum, dialect):
        if enum is None:
            return None
        return enum.value

    def process_result_value(self, value, dialect):
        if value is not None:
            return self._enum(value)
        return value
