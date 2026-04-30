import json
from typing import Optional, Any, Union, Dict, List

from app.config import redis_config
from redis.asyncio import Redis, ConnectionPool


class RedisClient:
    """Redis 客户端封装 - 自动 JSON 序列化"""

    _client: Optional[Redis] = None

    @classmethod
    async def init(cls) -> None:
        """初始化 Redis 连接池"""
        if cls._client is None:
            cls._client = Redis.from_pool(
                connection_pool=ConnectionPool(
                    host=redis_config.HOST,
                    port=redis_config.PORT,
                    password=redis_config.PASSWORD,
                    db=redis_config.DB,
                    decode_responses=redis_config.DECODE_RESPONSES,
                    socket_connect_timeout=redis_config.SOCKET_CONNECT_TIMEOUT,
                    socket_timeout=redis_config.SOCKET_TIMEOUT,
                    max_connections=redis_config.MAX_CONNECTIONS,
                )
            )

    @classmethod
    async def close(cls) -> None:
        """关闭 Redis 连接"""
        if cls._client is not None:
            await cls._client.close()
            cls._client = None

    @classmethod
    async def get_client(cls) -> Redis:
        """获取原始 Redis 客户端"""
        if cls._client is None:
            await cls.init()
        return cls._client

    async def set(
        self,
        key: str,
        value: Any,
        expire: Optional[int] = None,
    ) -> bool:
        """
        设置键值对
        
        Args:
            key: 键名
            value: 值 (dict/list 自动 JSON 序列化)
            expire: 过期时间（秒）
        """
        client = await self.get_client()
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value, ensure_ascii=False)
        result = await client.set(key, value, ex=expire)
        return result is True

    async def get(self, key: str, default: Any = None) -> Optional[Union[str, Dict, List]]:
        """获取键值，自动 JSON 反序列化"""
        client = await self.get_client()
        value = await client.get(key)
        if value is None:
            return default
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def delete(self, *keys: str) -> int:
        """删除一个或多个键"""
        if not keys:
            return 0
        client = await self.get_client()
        return await client.delete(*keys)

    async def exists(self, key: str) -> bool:
        """检查键是否存在"""
        client = await self.get_client()
        return await client.exists(key) > 0

    async def expire(self, key: str, expire: int) -> bool:
        """
        设置过期时间
        
        Args:
            key: 键名
            expire: 过期时间（秒）
        """
        client = await self.get_client()
        result = await client.expire(key, expire)
        return result is True

    async def ttl(self, key: str) -> int:
        """获取剩余过期时间（秒）"""
        client = await self.get_client()
        return await client.ttl(key)

    async def incr(self, key: str, amount: int = 1) -> int:
        """递增计数器"""
        client = await self.get_client()
        return await client.incr(key, amount)

    async def decr(self, key: str, amount: int = 1) -> int:
        """递减计数器"""
        client = await self.get_client()
        return await client.decr(key, amount)

    async def hset(self, key: str, field: str, value: Any) -> int:
        """哈希表设置字段"""
        client = await self.get_client()
        if isinstance(value, (dict, list, tuple)):
            value = json.dumps(value, ensure_ascii=False)
        return await client.hset(key, field, value)

    async def hget(self, key: str, field: str) -> Optional[Any]:
        """哈希表获取字段"""
        client = await self.get_client()
        value = await client.hget(key, field)
        if value is None:
            return None
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    async def hgetall(self, key: str) -> Dict[str, Any]:
        """获取哈希表所有字段"""
        client = await self.get_client()
        result = await client.hgetall(key)
        parsed = {}
        for k, v in result.items():
            try:
                parsed[k] = json.loads(v)
            except (json.JSONDecodeError, TypeError):
                parsed[k] = v
        return parsed


redis_client = RedisClient()
