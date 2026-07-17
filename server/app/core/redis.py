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

    async def hset(
        self,
        hash_key: str,
        mapping: Optional[Dict[str, Any]] = None,
        expire: Optional[int] = None,
    ) -> int:
        """
        Hash哈希表批量写入
        自动序列化dict/list/tuple为JSON字符串；仅本次写入数据时支持设置Hash过期时间

        Args:
            hash_key: Hash缓存键名，示例 open_admin:online_user:2
            mapping: 批量字段字典 {字段名: 值}，不传/空字典不执行写入
            expire: 过期秒数，>0 时为当前写入的Hash设置TTL；None/<=0 不操作过期

        Returns:
            int: 本次hset实际修改的字段数量
        """
        if not isinstance(hash_key, str) or not hash_key.strip():
            raise ValueError("hash_key 不能为空字符串")

        client = await self.get_client()
        modify_count = 0
        has_write = False

        if mapping and isinstance(mapping, dict):
            safe_map = {k: json.dumps(v, ensure_ascii=False) for k, v in mapping.items()}
            modify_count = await client.hset(hash_key, mapping=safe_map)
            has_write = True

        # 仅当本次执行了写入，且过期参数合法，才设置TTL
        if has_write and isinstance(expire, int) and expire > 0:
            try:
                await client.expire(hash_key, expire)
            except RedisError:
                # self.logger.warning(f"hash key {hash_key} 设置过期失败")
                pass

        return modify_count

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

    # ==================== ZSet 有序集合操作 ====================

    async def zadd(
        self,
        key: str,
        members: Dict[str, float],
        nx: bool = False,
        xx: bool = False,
    ) -> int:
        """
        添加成员到有序集合
        
        Args:
            key: 键名
            members: 成员字典 {member: score}
            nx: 仅添加不存在的成员
            xx: 仅更新已存在的成员
            
        Returns:
            新增的成员数量
        """
        client = await self.get_client()
        return await client.zadd(key, members, nx=nx, xx=xx)

    async def zrem(self, key: str, *members: str) -> int:
        """
        删除有序集合中的成员
        
        Args:
            key: 键名
            members: 要删除的成员
            
        Returns:
            成功删除的成员数量
        """
        if not members:
            return 0
        client = await self.get_client()
        return await client.zrem(key, *members)

    async def zscore(self, key: str, member: str) -> Optional[float]:
        """
        获取成员的分数
        
        Args:
            key: 键名
            member: 成员名
            
        Returns:
            成员分数，不存在返回 None
        """
        client = await self.get_client()
        return await client.zscore(key, member)

    async def zrank(self, key: str, member: str) -> Optional[int]:
        """
        获取成员的排名（从小到大）
        
        Args:
            key: 键名
            member: 成员名
            
        Returns:
            排名索引（从 0 开始），不存在返回 None
        """
        client = await self.get_client()
        return await client.zrank(key, member)

    async def zrevrank(self, key: str, member: str) -> Optional[int]:
        """
        获取成员的排名（从大到小）
        
        Args:
            key: 键名
            member: 成员名
            
        Returns:
            排名索引（从 0 开始），不存在返回 None
        """
        client = await self.get_client()
        return await client.zrevrank(key, member)

    async def zrange(
        self,
        key: str,
        start: int,
        end: int,
        withscores: bool = False,
    ) -> List:
        """
        按排名范围获取成员（从小到大）
        
        Args:
            key: 键名
            start: 起始索引
            end: 结束索引
            withscores: 是否返回分数
            
        Returns:
            成员列表或 (member, score) 元组列表
        """
        client = await self.get_client()
        return await client.zrange(key, start, end, withscores=withscores)

    async def zrevrange(
        self,
        key: str,
        start: int,
        end: int,
        withscores: bool = False,
    ) -> List:
        """
        按排名范围获取成员（从大到小）
        
        Args:
            key: 键名
            start: 起始索引
            end: 结束索引
            withscores: 是否返回分数
            
        Returns:
            成员列表或 (member, score) 元组列表
        """
        client = await self.get_client()
        return await client.zrevrange(key, start, end, withscores=withscores)

    async def zrangebyscore(
        self,
        key: str,
        min_score: Union[float, str],
        max_score: Union[float, str],
        start: Optional[int] = None,
        num: Optional[int] = None,
        withscores: bool = False,
    ) -> List:
        """
        按分数范围获取成员
        
        Args:
            key: 键名
            min_score: 最小分数（可用 '-inf' 表示负无穷）
            max_score: 最大分数（可用 '+inf' 表示正无穷）
            start: 分页起始位置
            num: 分页数量
            withscores: 是否返回分数
            
        Returns:
            成员列表或 (member, score) 元组列表
        """
        client = await self.get_client()
        return await client.zrangebyscore(
            key, min_score, max_score, start=start, num=num, withscores=withscores
        )

    async def zincrby(self, key: str, member: str, amount: float = 1.0) -> float:
        """
        增加成员的分数
        
        Args:
            key: 键名
            member: 成员名
            amount: 增加的分数（可为负数）
            
        Returns:
            增加后的分数
        """
        client = await self.get_client()
        return await client.zincrby(key, amount, member)

    async def zcard(self, key: str) -> int:
        """
        获取有序集合的成员数量
        
        Args:
            key: 键名
            
        Returns:
            成员数量
        """
        client = await self.get_client()
        return await client.zcard(key)

    async def zcount(
        self,
        key: str,
        min_score: Union[float, str],
        max_score: Union[float, str],
    ) -> int:
        """
        统计分数范围内的成员数量
        
        Args:
            key: 键名
            min_score: 最小分数
            max_score: 最大分数
            
        Returns:
            成员数量
        """
        client = await self.get_client()
        return await client.zcount(key, min_score, max_score)


redis_client = RedisClient()
