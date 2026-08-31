"""
LangGraph Redis Checkpointer 封装

基于 langgraph-checkpoint-redis 实现，提供：
- AsyncRedisSaver 单例管理
- 与项目 Redis 基础设施集成
- 延迟初始化（首次使用时才连接）

@since 2026-08-20
@version 1.0.1
"""

from typing import Optional
from langgraph.checkpoint.redis import AsyncRedisSaver

from app.config import redis_config
from app.core.logger import logger


class RedisCheckpointer:
    """
    Redis Checkpointer 工厂

    封装 langgraph-checkpoint-redis 的 AsyncRedisSaver，
    提供项目级单例访问。

    用法：
        saver = await RedisCheckpointer.get_instance()
        agent = ChatAgent(llm, prompt, checkpointer=saver)

    Note:
        - 依赖 RediSearch 模块（FT.* 命令）
        - 需在异步上下文中调用 get_instance()
        - 创建独立的 Redis 连接（decode_responses=False）
    """

    _instance: Optional[AsyncRedisSaver] = None
    _initialized: bool = False

    @classmethod
    async def get_instance(cls) -> AsyncRedisSaver:
        """
        获取 Redis Checkpointer 单例

        Returns:
            AsyncRedisSaver 实例
        """
        if cls._instance is None:
            cls._instance = await cls._create_saver()
        return cls._instance

    @classmethod
    def _build_redis_url(cls) -> str:
        """
        根据 redis_config 构造 Redis 连接 URL

        Returns:
            redis://[password@]host:port/db
        """
        auth = f"{redis_config.PASSWORD}@" if redis_config.PASSWORD else ""
        return f"redis://{auth}{redis_config.HOST}:{redis_config.PORT}/{redis_config.DB}"

    @classmethod
    async def _create_saver(cls) -> AsyncRedisSaver:
        """
        创建 AsyncRedisSaver 实例

        AsyncRedisSaver 的 BaseRedisSaver.__init__ 要求必须提供
        redis_url 或 redis_client 之一（不能仅传 connection_args）。
        本方法通过 redis_url 创建，并附加连接参数。
        """
        redis_url = cls._build_redis_url()
        connection_args = {
            "socket_connect_timeout": redis_config.SOCKET_CONNECT_TIMEOUT,
            "socket_timeout": redis_config.SOCKET_TIMEOUT,
            "decode_responses": False,  # checkpointer 需要原始字节
            "max_connections": redis_config.MAX_CONNECTIONS,
        }

        logger.info(f"初始化 Redis Checkpointer | url: {redis_config.HOST}:{redis_config.PORT}/{redis_config.DB}")

        # 通过 redis_url 创建 saver（满足 BaseRedisSaver 的参数要求）
        saver = AsyncRedisSaver(redis_url=redis_url, connection_args=connection_args)

        # 异步初始化：创建 RediSearch 索引
        try:
            await saver.asetup()
            logger.info("Redis Checkpointer 初始化成功（RediSearch 索引已创建）")
            cls._initialized = True
        except Exception as e:
            logger.warning(f"Redis Checkpointer asetup 失败（可能缺少 RediSearch 模块）: {e}")
            logger.info("将跳过 RediSearch 索引创建，仅使用基础 Redis 功能")
            # 即使 asetup 失败，仍可使用基础功能（put/get），
            # 但 list/search 等索引相关功能可能不可用

        return saver

    @classmethod
    async def aclose(cls) -> None:
        """关闭连接（应用关闭时调用）"""
        if cls._instance is not None:
            try:
                # AsyncRedisSaver 没有 aclose，通过底层 redis 客户端关闭
                if hasattr(cls._instance, '_redis'):
                    await cls._instance._redis.aclose()
            except Exception:
                pass
            cls._instance = None
            cls._initialized = False
            logger.info("Redis Checkpointer 已关闭")

    @classmethod
    async def delete_thread(cls, thread_id: str) -> None:
        """
        删除指定会话的 checkpoint 数据

        用于会话删除时联动清理 LangGraph Agent 记忆，
        避免残留孤儿 checkpoint 数据。

        Args:
            thread_id: 会话 ID（与 session_id 一致）
        """
        if cls._instance is None:
            return
        try:
            await cls._instance.adelete_thread(thread_id)
            logger.info(f"删除 checkpoint 数据 | thread_id: {thread_id}")
        except Exception as e:
            logger.warning(f"删除 checkpoint 数据失败 | thread_id: {thread_id} | error: {e}")

    @classmethod
    def is_initialized(cls) -> bool:
        """检查是否已初始化"""
        return cls._initialized
