from datetime import datetime, timezone
from pydantic import BaseModel, Field, field_serializer, field_validator
from typing import Optional, Any


class CaptchaResponse(BaseModel):
    """验证码响应"""
    captcha_id: str = Field(..., description="验证码唯一标识")
    captcha_image: str = Field(..., description="验证码图片Base64编码")

class CaptchaVerifyRequest(BaseModel):
    """验证码验证请求"""
    captcha_id: str = Field(..., description="验证码唯一标识")
    captcha_code: str = Field(..., description="验证码")

class TokenPayload(BaseModel):
    """Token有效载荷"""
    sub: str = Field(..., description="用户ID")
    type: str = Field(..., description="令牌类型: access/refresh")
    exp: datetime = Field(..., description="过期时间")
    iat: datetime = Field(..., description="签发时间")

    @field_validator('exp', 'iat', mode='before')
    @classmethod
    def int_to_datetime(cls, v: int | datetime) -> datetime:
        if isinstance(v, int):
            return datetime.fromtimestamp(v, tz=timezone.utc).replace(tzinfo=None)
        return v

    @field_serializer('exp', 'iat')
    def serialize_datetime(self, v: datetime) -> int:
        return int(v.timestamp())


class TokenResponse(BaseModel):
    """Token响应"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(..., description="访问令牌过期时间（秒）")


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class PasswordLoginRequest(BaseModel):
    """密码登录请求"""
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    captcha_code: Optional[str] = Field(None, description="验证码")
