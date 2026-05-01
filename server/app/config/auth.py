from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict
from pydantic import Field


class AuthConfig(BaseConfig):
    """认证配置"""
    JWT_SECRET_KEY: str = "your-secret-key-change-in-production-please-use-openssl-rand-hex-32"
    JWT_REFRESH_SECRET_KEY: str = "your-refresh-secret-key-change-in-production-please-use-openssl-rand-hex-32"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ==================== 登录失败锁定配置 ====================
    MAX_LOGIN_ATTEMPTS: int = Field(default=3, description="最大密码尝试次数，超过则锁定账号")
    ACCOUNT_LOCK_DURATION_MINUTES: int = Field(default=30, description="锁定时长（分钟，默认 30 分钟）")

    model_config = SettingsConfigDict(
        env_prefix="AUTH_"
    )

auth_config = AuthConfig()
