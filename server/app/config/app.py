from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class AppConfig(BaseConfig):
    """应用配置类"""
    # 应用基本配置
    NAME: str = "OpenAdmin"
    VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 文档配置
    DOCS_ENABLE: bool = True  # 是否开启 API 文档
    DOCS_TITLE: str = "OpenAdmin 后台管理系统"
    DOCS_DESCRIPTION: str = "基于 FastAPI + Vue3 开发的开源后台管理系统，提供完整的用户管理、权限控制、数据管理等功能。"
    DOCS_VERSION: str = "1.0.0"
    DOCS_CONTACT_NAME: str = "sjzhao"
    DOCS_CONTACT_EMAIL: str = "1500492856@qq.com"
    DOCS_URL: str = "/docs"
    REDOC_URL: str = "/redoc"
    
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
