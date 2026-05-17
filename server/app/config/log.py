from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class LogConfig(BaseConfig):
    """日志配置类"""
    
    # 日志级别配置
    STDOUT_LEVEL: str = "DEBUG"  # 控制台日志级别
    FILE_LEVEL: str = "INFO"  # 文件日志级别
    
    # 日志目录配置
    DIR: str = "logs"  # 日志存储目录
    
    # 日志文件配置（轮转策略、保留时间、压缩格式）
    ROTATION: str = "00:00"  # 日志文件轮转时间（每天凌晨0点）
    RETENTION: str = "30 days"  # 日志保留时间
    COMPRESSION: str = "zip"  # 日志压缩格式
    
    # 日志格式配置
    JSON_FORMAT: bool = False  # 是否使用 JSON 格式输出
    
    # 调试信息配置
    DIAGNOSE: bool = True  # 是否显示诊断信息（包含变量值）
    BACKTRACE: bool = True  # 是否显示完整回溯信息
    
    model_config = SettingsConfigDict(
        env_prefix="LOG_"
    )


log_config = LogConfig()