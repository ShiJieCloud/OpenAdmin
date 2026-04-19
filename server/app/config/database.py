from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class DatabaseConfig(BaseConfig):
    """数据库配置类"""
    HOST: str = "localhost"
    PORT: int = 3306
    USER: str = "root"
    PASSWORD: str = "password"
    NAME: str = "openadmin"
    CHARSET: str = "utf8mb4"
    POOL_SIZE: int = 10
    MAX_OVERFLOW: int = 20
    DEBUG: bool = True
    
    model_config = SettingsConfigDict(
        env_prefix="DB_"
    )

database_config = DatabaseConfig()
