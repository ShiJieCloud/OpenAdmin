from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.datebase import get_db_session, get_redis
from app.services import UserService, PermissionService
from app.core.redis import RedisClient


async def get_user_service(
    db_session: AsyncSession = Depends(get_db_session),
    redis_client: RedisClient = Depends(get_redis)
) -> UserService:
    """用户服务依赖注入，返回 UserService 实例"""
    return UserService(db_session, redis_client)


async def get_permission_service(
    db_session: AsyncSession = Depends(get_db_session)
) -> PermissionService:
    """权限服务依赖注入，返回 PermissionService 实例"""
    return PermissionService(db_session)
