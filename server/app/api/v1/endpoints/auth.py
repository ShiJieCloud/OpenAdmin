from fastapi import APIRouter, Depends, UploadFile, File

from app.core.response import ResponseBuilder
from app.deps.auth import get_current_active_user
from app.deps.service import get_user_service, get_user_apply_service, get_captcha_service
from app.models.user import User
from app.schemas.base.response import ApiResponse
from app.schemas import (
    UserInfoResponse,
    UserApplyInfoResponse,
    PasswordLoginRequest,
    RegisterRequest,
    RefreshTokenRequest,
    TokenResponse,
    CaptchaResponse
)
from app.services import UserService, UserApplyService, CaptchaService

router = APIRouter()


@router.post(
    "/login/password", 
    response_model=ApiResponse[TokenResponse],
    summary="账号密码登录",
    description="使用账号密码登录系统，返回登录令牌"
)
async def password_login(
    req: PasswordLoginRequest,
    user_service: UserService = Depends(get_user_service),
    captcha_service: CaptchaService = Depends(get_captcha_service)
):
    """账号密码登录"""
    await captcha_service.verify_captcha(req.captcha_id, req.captcha_code)
    token = await user_service.login_password(req)
    return ResponseBuilder.success(token)


@router.post(
    "/register",
    response_model=ApiResponse[UserApplyInfoResponse],
    summary="用户注册",
    description="提交用户注册申请，写入待审批记录（不创建正式账号），需等待管理员审批通过后即可登录"
)
async def register(
    req: RegisterRequest,
    apply_service: UserApplyService = Depends(get_user_apply_service)
):
    """提交用户注册申请

    走审批制注册流程：仅校验用户名/手机号唯一性并写入 sys_user_apply 申请表，
    status=0 待审核，不创建正式系统用户，也不签发 Token。
    用户需等待管理员审批通过后，凭账号密码走登录流程获取 Token。
    """
    apply = await apply_service.create_apply(req)
    apply_info = UserApplyInfoResponse.model_validate(apply)
    return ResponseBuilder.success(apply_info, message="注册申请提交成功，请等待管理员审批")


@router.post(
    "/login/face",
    response_model=ApiResponse[TokenResponse],
    summary="人脸识别登录",
    description="上传摄像头抓拍的人脸图片进行识别登录，返回登录令牌。\n"
                "⚠️ 仅人脸特征比对，无活体防护，静态照片可冒充登录；生产建议接入动作活体，外网谨慎开放。"
)
async def face_login(
    face_image: UploadFile = File(..., description="人脸图片"),
    user_service: UserService = Depends(get_user_service)
):
    """
    人脸识别登录

    ⚠️ 仅执行人脸特征比对，无防照片攻击能力，静态照片可冒充登录。
    生产环境建议接入动作活体检测；外网环境谨慎开放人脸登录。
    """

    token = await user_service.login_face(face_image)
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
    await user_service.clean_user_online_session(user.id)
    return ResponseBuilder.success(message="退出登录成功")


@router.get("/captcha", response_model=ApiResponse[CaptchaResponse])
async def get_captcha(
    captcha_service: CaptchaService = Depends(get_captcha_service)
):
    """获取验证码"""
    captcha = await captcha_service.generate_captcha()
    return ResponseBuilder.success(captcha)


@router.get("/me", response_model=ApiResponse[UserInfoResponse])
async def get_current_user_info(
    user: User = Depends(get_current_active_user)
):
    """获取当前登录用户信息"""
    user_info = UserInfoResponse.model_validate(user)
    return ResponseBuilder.success(user_info)
