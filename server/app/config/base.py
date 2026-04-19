from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class BaseConfig(BaseSettings):
    """基础配置类，定义读取环境变量的规则
    
    支持加载多个环境变量文件，优先级从低到高（后面的会覆盖前面的）：
    1. .env - 基础配置文件
    2. .env.{ENV} - 环境特定配置文件（如 .env.dev, .env.prod）
    """
    env_name: str = os.getenv("ENV", "dev")
    default_env_path: str = ".env/.env"
    env_file_path: str = f".env/.env.{env_name}"
    
    model_config = SettingsConfigDict(
        env_file=[
            default_env_path,
            env_file_path
        ],
        case_sensitive=False,
        env_file_encoding="utf-8",
        extra="ignore" # 忽略额外的环境变量
    )
