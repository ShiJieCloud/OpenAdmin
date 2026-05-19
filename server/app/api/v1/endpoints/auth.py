from fastapi import APIRouter, Depends

from app.core.response import ResponseBuilder
from app.deps.auth import get_current_active_user
from app.deps.service import get_user_service, get_captcha_service
from app.models.user import User
from app.schemas.base.response import ApiResponse
from app.schemas import (
    UserInfoResponse,
    PasswordLoginRequest, 
    RefreshTokenRequest, 
    TokenResponse, 
    CaptchaVerifyRequest, 
    CaptchaResponse
)
from app.services import UserService, CaptchaService

router = APIRouter()


@router.post(
    "/login/password", 
    response_model=ApiResponse[TokenResponse],
    summary="账号密码登录",
    description="使用账号密码登录系统，返回登录令牌"
)
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


@router.post("/logout", response_model=ApiResponse[None])
async def logout(
    user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """退出登录"""
    await user_service.logout(user.id)
    return ResponseBuilder.success(message="退出登录成功")


@router.get("/captcha", response_model=ApiResponse[CaptchaResponse])
async def get_captcha(
    captcha_service: CaptchaService = Depends(get_captcha_service)
):
    """获取验证码"""
    captcha = await captcha_service.generate_captcha()
    return ResponseBuilder.success(captcha)


@router.post("/captcha/verify", response_model=ApiResponse[None])
async def verify_captcha(
    req: CaptchaVerifyRequest,
    captcha_service: CaptchaService = Depends(get_captcha_service)
):
    """验证验证码"""
    await captcha_service.verify_captcha(req.captcha_id, req.captcha_code)
    return ResponseBuilder.success(message="验证码验证成功")


@router.get("/me", response_model=ApiResponse[UserInfoResponse])
async def get_current_user_info(
    user: User = Depends(get_current_active_user)
):
    """获取当前登录用户信息"""
    user_info = UserInfoResponse.model_validate(user)
    return ResponseBuilder.success(user_info)
