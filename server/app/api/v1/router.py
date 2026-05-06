from fastapi import APIRouter, Depends

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as user_router
from app.api.v1.endpoints.role import router as role_router
from app.api.v1.endpoints.menu import router as menu_router


api_v1_router = APIRouter()

api_v1_router.include_router(user_router, prefix="/user", tags=["用户管理"])
api_v1_router.include_router(role_router, prefix="/role", tags=["角色管理"])
api_v1_router.include_router(menu_router, prefix="/menu", tags=["菜单管理"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["认证授权"])   
