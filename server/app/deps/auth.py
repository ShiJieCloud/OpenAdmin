from app.core.enums import UserStatusEnum, RespCodeEnum
from app.core.security import verify_access_token
from app.models import User
from fastapi import Depends
from app.schemas.auth import TokenPayload
from app.services.user import UserService
from .service import get_user_service
from app.core.exceptions import BusinessError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials


security = HTTPBearer()


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> TokenPayload:
    """
    验证 Access Token 是否有效
    
    Args:
        token: Access Token
    
    Raises:
        BusinessError: Token 无效或过期
    """

    token = credentials.credentials

    return verify_access_token(token)
    
async def get_current_user(
    token: TokenPayload = Depends(verify_token),
    user_service: UserService = Depends(get_user_service)
) -> User:
    """
    获取当前用户信息
    
    Args:
        token: 验证后的 Token
    
    Returns:
        User: 当前用户信息
    """

    return await user_service.get_user(id=token.sub)

async def get_current_active_user(
    user: User = Depends(get_current_user)
) -> User:
    """
    获取当前活跃用户信息（校验用户状态是否正常）
    
    Args:
        user: 当前用户信息
    
    Returns:
        User: 当前活跃用户信息
    """

    if not UserStatusEnum.is_normal(user.status):
        raise BusinessError(RespCodeEnum.USER_STATUS_ERROR)

    return user
