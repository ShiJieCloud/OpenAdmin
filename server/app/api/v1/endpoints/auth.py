from fastapi import APIRouter, Depends

from app.core.response import ResponseBuilder
from app.deps.service import get_user_service
from app.schemas.auth import PasswordLoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.base.response import ApiResponse
from app.services.user import UserService

router = APIRouter()


@router.post("/login/password", response_model=ApiResponse[TokenResponse])
async def password_login(
    req: PasswordLoginRequest,
    user_service: UserService = Depends(get_user_service)
):
    """账号密码登录"""
    token = await user_service.login_password(req)
    return ResponseBuilder.success(token)


@router.post("/refresh-token", response_model=ApiResponse[TokenResponse])
async def refresh_token(
    req: RefreshTokenRequest,
    user_service: UserService = Depends(get_user_service)
):
    """刷新令牌"""
    token = await user_service.refresh_token(req)
    return ResponseBuilder.success(token)
