import warnings
from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from jose import JWTError, jwt, ExpiredSignatureError
from passlib.context import CryptContext

from app.config import auth_config
from app.core.enums import RespCodeEnum, TokenTypeEnum
from app.core.exceptions import BusinessError
from app.schemas.auth import TokenPayload


# ========================== 密码加密 ==========================

# 忽略passlib警告
warnings.filterwarnings("ignore", category=UserWarning, module="passlib.handlers.bcrypt")

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """密码加密"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """密码校验"""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except (ValueError, TypeError):
        # TODO: 打印异常信息
        return False


# ========================== JWT 令牌 ==========================


def create_token(
    subject: int,
    token_type: TokenTypeEnum,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """创建 JWT 令牌"""

    # 过期时间 (使用带时区的 UTC 时间，避免 timestamp 计算错误)
    now = datetime.now(timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        if token_type == TokenTypeEnum.ACCESS:
            expire = now + timedelta(minutes=auth_config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
        else:
            expire = now + timedelta(days=auth_config.JWT_REFRESH_TOKEN_EXPIRE_DAYS)

    # 载荷
    payload = TokenPayload(
        sub=str(subject),
        type=token_type,
        exp=expire,
        iat=now,
    )
    
    # 密钥
    secret_key = (
        auth_config.JWT_SECRET_KEY
        if token_type is TokenTypeEnum.ACCESS
        else auth_config.JWT_REFRESH_SECRET_KEY
    )

    # 签发
    return jwt.encode(
        payload.model_dump(),
        secret_key,
        algorithm=auth_config.JWT_ALGORITHM
    )


def create_access_token(user_id: int) -> str:
    """创建访问令牌"""
    return create_token(user_id, TokenTypeEnum.ACCESS)


def create_refresh_token(user_id: int) -> str:
    """创建刷新令牌"""
    
    return create_token(user_id, TokenTypeEnum.REFRESH)


def create_tokens(user_id: int) -> tuple[str, str]:
    """创建访问令牌和刷新令牌"""
    access_token = create_access_token(user_id)
    refresh_token = create_refresh_token(user_id)
    return access_token, refresh_token


def verify_token(token: str, token_type: TokenTypeEnum) -> TokenPayload:
    """验证 Token 并返回载荷模型"""
    
    # 密钥
    secret_key = (
        auth_config.JWT_SECRET_KEY
        if token_type is TokenTypeEnum.ACCESS
        else auth_config.JWT_REFRESH_SECRET_KEY
    )

    try:
        # 解码
        payload_dict = jwt.decode(
            token,
            secret_key,
            algorithms=[auth_config.JWT_ALGORITHM],
            options={"verify_exp": True} # 校验过期时间
        )

        # 模型校验（自动校验字段是否完整、格式正确）
        payload = TokenPayload(**payload_dict)

        # 校验类型
        if payload.type != token_type.value:
            raise BusinessError(RespCodeEnum.TOKEN_TYPE_ERROR)

        return payload

    except ExpiredSignatureError:
        raise BusinessError(RespCodeEnum.TOKEN_EXPIRED)
    except JWTError:
        raise BusinessError(RespCodeEnum.TOKEN_INVALID)


def verify_access_token(token: str) -> TokenPayload:
    """验证访问令牌"""
    return verify_token(token, TokenTypeEnum.ACCESS)


def verify_refresh_token(token: str) -> TokenPayload:
    """验证刷新令牌"""
    return verify_token(token, TokenTypeEnum.REFRESH)
