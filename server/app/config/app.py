from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class AppConfig(BaseConfig):
    """应用配置类"""
    # 应用基本配置
    NAME: str = "OpenAdmin"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # CORS 跨域配置
    CORS_ALLOW_ORIGINS: list[str] = ["*"]  # 允许的来源域名列表
    CORS_ALLOW_CREDENTIALS: bool = True  # 是否允许携带凭证
    CORS_ALLOW_METHODS: list[str] = ["*"]  # 允许的 HTTP 方法列表
    CORS_ALLOW_HEADERS: list[str] = ["*"]  # 允许的 HTTP 头列表
    CORS_EXPOSE_HEADERS: list[str] = []  # 暴露的 HTTP 头列表
    CORS_MAX_AGE: int = 600  # 预检请求的缓存时间（秒）

    model_config = SettingsConfigDict(
        env_prefix="APP_"
    )

app_config = AppConfig()
