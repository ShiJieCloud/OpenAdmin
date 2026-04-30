from app.core.redis import redis_client, RedisClient


async def get_redis() -> RedisClient:
    """
    获取 RedisClient 封装实例
    
    推荐使用此依赖注入，直接调用封装的方法:
        - redis.set(key, value) 自动 JSON 序列化
        - redis.get(key) 自动 JSON 反序列化
        - 其他便捷方法...
    """
    return redis_client
