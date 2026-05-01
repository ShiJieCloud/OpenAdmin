from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.datebase import get_db_session, get_redis
from app.services.user import UserService
from app.core.redis import RedisClient


async def get_user_service(
    db_session: AsyncSession = Depends(get_db_session),
    redis_client: RedisClient = Depends(get_redis)
) -> UserService:
    """用户服务依赖注入，返回 UserService 实例"""
    return UserService(db_session, redis_client)
