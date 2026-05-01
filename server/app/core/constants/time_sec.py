from enum import IntEnum


class TimeSec(IntEnum):
    """
    时间秒数常量
    统一管理所有时间配置，避免硬编码魔法数字
    """

    # ==================== 基础单位 ====================
    SECOND = 1
    MINUTE = 60
    HOUR = 60 * 60
    DAY = 24 * 60 * 60
