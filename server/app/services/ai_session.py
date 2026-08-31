"""
会话存储服务

基于 Redis 实现的会话元数据和消息历史存储，用于：
- 会话列表展示（前端左侧会话列表）
- 消息历史加载（切换会话时恢复历史消息）
- 会话 CRUD 操作

Redis Key 设计（遵循 RedisKeyTemplate 规范，统一 open_admin 前缀）：
- open_admin:ai_sessions:{user_id}     ZSet   会话列表索引（score=updated_at 时间戳）
- open_admin:ai_session:{session_id}   Hash   会话元数据（title/user_id/created_at/updated_at）
- open_admin:ai_messages:{session_id}   List   消息历史（每个元素是 JSON 字符串）

@since 2026-08-20
@version 1.0.0
"""

import json
import time
from typing import Optional

from app.core.redis import RedisClient
from app.core.constants.redis_keys import RedisKeyTemplate
from app.core.logger import logger
from app.schemas.ai_session import SessionMeta, SessionMessage


class AiSessionService:
    """
    基于 Redis 的会话存储服务

    职责：
    1. 会话元数据管理（创建/更新/删除/查询）
    2. 消息历史存储（保存/查询）
    3. 会话列表索引（按用户查询/按时间排序）

    与 LangGraph Checkpointer 的区别：
    - Checkpointer 存储 Agent 内部序列化状态（二进制/复杂结构）
    - AiSession 存储可读的会话元数据和消息（用于前端展示）
    """

    def __init__(self, redis_client: RedisClient):
        self._redis_client = redis_client

    async def create_session(
        self, session_id: str, user_id: int
    ) -> SessionMeta:
        """
        创建新会话

        Args:
            session_id: 会话 ID（由 uuid4().hex 生成）
            user_id: 用户 ID

        Returns:
            创建的会话元数据
        """
        now = time.time()
        meta = SessionMeta(
            session_id=session_id,
            title="新对话",
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )

        # 存储元数据到 Hash
        meta_key = RedisKeyTemplate.ai_session(session_id)
        mapping = {
            "title": meta.title,
            "user_id": str(user_id),
            "created_at": str(now),
            "updated_at": str(now),
        }
        await self._redis_client.hset(meta_key, mapping=mapping)

        # 添加到用户的会话列表索引（ZSet）
        list_key = RedisKeyTemplate.ai_sessions(user_id)
        await self._redis_client.zadd(list_key, {session_id: now})

        logger.info(f"创建会话 | session_id: {session_id} | user_id: {user_id}")
        return meta

    async def get_session(self, session_id: str) -> Optional[SessionMeta]:
        """
        获取会话元数据

        Args:
            session_id: 会话 ID

        Returns:
            会话元数据，不存在返回 None
        """
        meta_key = RedisKeyTemplate.ai_session(session_id)
        data = await self._redis_client.hgetall(meta_key)
        if not data:
            return None
        return SessionMeta(
            session_id=session_id,
            title=data.get("title", "新对话"),
            user_id=int(data.get("user_id", 0)),
            created_at=float(data.get("created_at", 0)),
            updated_at=float(data.get("updated_at", 0)),
        )

    async def list_user_sessions(
        self, user_id: int, limit: int = 100
    ) -> list[SessionMeta]:
        """
        获取用户的会话列表（按更新时间倒序）

        Args:
            user_id: 用户 ID
            limit: 返回数量上限

        Returns:
            会话元数据列表（按 updated_at 降序）
        """
        list_key = RedisKeyTemplate.ai_sessions(user_id)
        session_ids = await self._redis_client.zrevrange(list_key, 0, limit - 1)

        sessions = []
        for sid in session_ids:
            meta = await self.get_session(sid)
            if meta:
                sessions.append(meta)
        return sessions

    async def update_session(
        self, session_id: str, title: Optional[str] = None
    ) -> None:
        """
        更新会话信息

        Args:
            session_id: 会话 ID
            title: 新标题（可选）
        """
        meta_key = RedisKeyTemplate.ai_session(session_id)
        mapping = {"updated_at": str(time.time())}
        if title:
            mapping["title"] = title
        await self._redis_client.hset(meta_key, mapping=mapping)

        # 更新 ZSet 中的 score（刷新排序）
        meta = await self.get_session(session_id)
        if meta:
            list_key = RedisKeyTemplate.ai_sessions(meta.user_id)
            await self._redis_client.zadd(list_key, {session_id: time.time()})

    async def delete_session(self, session_id: str, user_id: int) -> None:
        """
        删除会话及其所有数据

        Args:
            session_id: 会话 ID
            user_id: 用户 ID
        """
        # 删除元数据
        meta_key = RedisKeyTemplate.ai_session(session_id)
        await self._redis_client.delete(meta_key)

        # 删除消息历史
        messages_key = RedisKeyTemplate.ai_messages(session_id)
        await self._redis_client.delete(messages_key)

        # 从用户列表索引移除
        list_key = RedisKeyTemplate.ai_sessions(user_id)
        await self._redis_client.zrem(list_key, session_id)

        logger.info(f"删除会话 | session_id: {session_id} | user_id: {user_id}")

    async def save_message(
        self, session_id: str, message: SessionMessage
    ) -> None:
        """
        保存消息到会话

        Args:
            session_id: 会话 ID
            message: 聊天消息
        """
        messages_key = RedisKeyTemplate.ai_messages(session_id)
        msg_json = json.dumps({
            "role": message.role,
            "content": message.content,
            "reasoning_content": message.reasoning_content,
            "model_id": message.model_id,
            "timestamp": message.timestamp,
        }, ensure_ascii=False)
        await self._redis_client.rpush(messages_key, msg_json)

        # 更新会话时间
        await self.update_session(session_id)

    async def save_round_messages(
        self,
        session_id: str,
        model_id: str,
        user_message: str,
        ai_response: str,
        ai_reasoning: str = "",
    ) -> None:
        """
        流式完成后保存本轮用户消息与 AI 回复

        Args:
            session_id: 会话 ID
            model_id: 模型标识
            user_message: 用户消息内容
            ai_response: AI 回复内容
            ai_reasoning: AI 推理内容
        """
        try:
            now = time.time()

            # 保存用户消息
            await self.save_message(
                session_id,
                SessionMessage(
                    role="user",
                    content=user_message,
                    model_id=model_id,
                    timestamp=now,
                ),
            )

            # 保存 AI 回复
            await self.save_message(
                session_id,
                SessionMessage(
                    role="assistant",
                    content=ai_response,
                    reasoning_content=ai_reasoning or None,
                    model_id=model_id,
                    timestamp=now,
                ),
            )

            # 更新会话标题（首次对话时用第一条用户消息作为标题）
            meta = await self.get_session(session_id)
            if meta and meta.title == "新对话":
                title = user_message[:20] if user_message else "新对话"
                await self.update_session(session_id, title=title)

            logger.debug(f"消息持久化完成 | session: {session_id}")
        except Exception as e:
            logger.error(f"消息持久化失败: {e}")

    async def get_messages(
        self, session_id: str, limit: int = 200
    ) -> list[SessionMessage]:
        """
        获取会话的消息历史

        Args:
            session_id: 会话 ID
            limit: 返回数量上限

        Returns:
            消息列表（按时间顺序）
        """
        messages_key = RedisKeyTemplate.ai_messages(session_id)
        raw_messages = await self._redis_client.lrange(messages_key, 0, limit - 1)

        messages = []
        for raw in raw_messages:
            try:
                data = json.loads(raw)
                messages.append(SessionMessage(
                    role=data["role"],
                    content=data["content"],
                    reasoning_content=data.get("reasoning_content"),
                    model_id=data.get("model_id", ""),
                    timestamp=data.get("timestamp", 0),
                ))
            except (json.JSONDecodeError, KeyError) as e:
                logger.warning(f"解析消息历史失败: {e}")
                continue

        return messages
