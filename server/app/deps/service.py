from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.datebase import get_db_session, get_redis
from app.services import (
    UserService,
    PermissionService,
    RoleService,
    PostService,
    MenuService,
    LoginLogService,
    OperLogService,
    CaptchaService
)
from app.core.redis import RedisClient


async def get_user_service(
    db_session: AsyncSession = Depends(get_db_session),
    redis_client: RedisClient = Depends(get_redis)
) -> UserService:
    """用户服务依赖注入，返回 UserService 实例"""
    return UserService(db_session, redis_client)


async def get_captcha_service(
    redis_client: RedisClient = Depends(get_redis)
) -> CaptchaService:
    """验证码服务依赖注入，返回 CaptchaService 实例"""
    return CaptchaService(redis_client)


async def get_permission_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> PermissionService:
    """权限服务依赖注入，返回 PermissionService 实例"""
    return PermissionService(db_session)


async def get_role_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> RoleService:
    """角色服务依赖注入，返回 RoleService 实例"""
    return RoleService(db_session)


async def get_post_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> PostService:
    """岗位服务依赖注入，返回 PostService 实例"""
    return PostService(db_session)


async def get_menu_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> MenuService:
    """菜单服务依赖注入，返回 MenuService 实例"""
    return MenuService(db_session)


async def get_login_log_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> LoginLogService:
    """登录日志服务依赖注入，返回 LoginLogService 实例"""
    return LoginLogService(db_session)


async def get_oper_log_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> OperLogService:
    """操作日志服务依赖注入，返回 OperLogService 实例"""
    return OperLogService(db_session)
