from enum import IntEnum


class UserStatusEnum(IntEnum):
    """
    用户状态枚举

    说明：
        用于统一管理用户账号的所有状态
        配合状态变更流程使用
    枚举值：
        - 0: 账号可正常使用
        - 1: 管理员手动禁用
        - 2: 登录失败次数过多，可自动解锁
        - 3: 用户主动注销，不可逆
        - 4: 风控或违规操作冻结
    """
    NORMAL = 0 
    DISABLED = 1
    LOCKED = 2
    CANCELLED = 3
    FROZEN = 4

    @classmethod
    def is_normal(cls, status: int) -> bool:
        """检查用户状态是否正常"""
        return status == cls.NORMAL
