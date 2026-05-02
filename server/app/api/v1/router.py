from fastapi import APIRouter, Depends

from app.api.v1.endpoints.auth import router as auth_router
from app.api.v1.endpoints.user import router as user_router
from app.deps import get_current_user, has_any_role



api_v1_router = APIRouter()

api_v1_router.include_router(user_router, prefix="/user", tags=["用户管理"])
api_v1_router.include_router(auth_router, prefix="/auth", tags=["认证授权"])   
