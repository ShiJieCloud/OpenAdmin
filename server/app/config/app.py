from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class AppConfig(BaseConfig):
    """应用配置类"""
    # 应用基本配置
    NAME: str = "OpenAdmin"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    model_config = SettingsConfigDict(
        env_prefix="APP_"
    )

app_config = AppConfig()
