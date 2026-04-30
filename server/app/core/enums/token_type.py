from enum import StrEnum


class TokenTypeEnum(StrEnum):
    """Token类型枚举"""
    ACCESS = "access"  # 访问令牌
    REFRESH = "refresh"  # 刷新令牌
