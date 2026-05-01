from typing import AsyncGenerator

from app.core.redis import redis_client, RedisClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal


async def get_redis() -> RedisClient:
    """
    获取 RedisClient 封装实例
    
    推荐使用此依赖注入，直接调用封装的方法:
        - redis.set(key, value) 自动 JSON 序列化
        - redis.get(key) 自动 JSON 反序列化
        - 其他便捷方法...
    """
    return redis_client

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    异步会话依赖注入
    供 Service 依赖、接口参数注入使用
    自动管理事务：成功时提交，异常时回滚
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
