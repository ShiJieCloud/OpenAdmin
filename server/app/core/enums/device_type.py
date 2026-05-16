from enum import StrEnum


class DeviceTypeEnum(StrEnum):
    """设备类型枚举"""
    PC = "PC"             # 电脑端（Windows/Mac/Linux 桌面设备）
    PHONE = "PHONE"       # 手机（安卓手机、iPhone）
    PAD = "PAD"           # 平板（iPad、安卓平板）
    TV = "TV"             # 智能电视 / 电视盒子
    CAR = "CAR"           # 车载车机设备
    WATCH = "WATCH"       # 智能手表
    ROBOT = "ROBOT"       # 爬虫、脚本、接口恶意登录、机器访问
    UNKNOWN = "UNKNOWN"   # 无法识别 UA、空 UA、异常设备
