from enum import Enum


class AppEnv(str, Enum):
    DEV = "dev"
    TEST = "test"
    PROD = "prod"


class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"


class RoleCode(str, Enum):
    ANONYMOUS = "anonymous"
    USER = "user"
    CREATOR = "creator"
    ADMIN = "admin"
