from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class AuthConfig(BaseConfig):
    """认证配置"""
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-please-use-openssl-rand-hex-32"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production-please-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_prefix="AUTH_"
    )

auth_config = AuthConfig()