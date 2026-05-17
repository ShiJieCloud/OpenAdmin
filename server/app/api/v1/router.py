from fastapi import APIRouter

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.role import router as role_router
from app.api.v1.endpoints.menu import router as menu_router
from app.api.v1.endpoints.login_log import router as login_log_router
from app.api.v1.endpoints.oper_log import router as oper_log_router


api_v1_router = APIRouter()

api_v1_router.include_router(user_router, prefix="/user", tags=["用户管理"])
api_v1_router.include_router(role_router, prefix="/role", tags=["角色管理"])
api_v1_router.include_router(menu_router, prefix="/menu", tags=["菜单管理"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["认证授权"])
api_v1_router.include_router(login_log_router, prefix="/login-log", tags=["登录日志"])
api_v1_router.include_router(oper_log_router, prefix="/oper-log", tags=["操作日志"])   
