from enum import Enum


class EnumHasValue(Enum):
    @classmethod
    def has_value(cls, value):
        return value in cls._value2member_map_ 

class UserRole(EnumHasValue):
    ADMIN = "admin"
    USER = "user"

