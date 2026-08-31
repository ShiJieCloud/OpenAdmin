"""
AI 会话持久化数据结构与响应模型

定义 AiSession 服务使用的内部数据结构与 HTTP 响应模型：
- SessionMeta：会话元数据（dataclass，对应 Redis Hash）
- SessionMessage：会话消息记录（dataclass，对应 Redis List 元素）
- AiChatSessionResponse：会话列表响应项（Pydantic，从 SessionMeta 转换，省略 user_id/model_id）
- AiChatMessageResponse：会话消息响应项（Pydantic，从 SessionMessage 转换）

与 schemas/ai_chat.py 的区别：
- ai_chat.ChatMessage 是 HTTP 请求体（Pydantic BaseModel，仅含 content）
- 本模块的 SessionMessage 是持久化记录（dataclass，含 timestamp/model_id 等元数据）

@since 2026-08-20
@version 1.0.0
"""

from dataclasses import dataclass
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


@dataclass
class SessionMeta:
    """会话元数据"""
    session_id: str
    title: str
    user_id: int
    created_at: float
    updated_at: float


@dataclass
class SessionMessage:
    """会话消息记录"""
    role: str
    content: str
    reasoning_content: Optional[str] = None
    model_id: str = ""
    timestamp: float = 0


class AiChatSessionResponse(BaseModel):
    """会话列表响应项"""
    model_config = ConfigDict(from_attributes=True)
    session_id: str = Field(..., description="会话ID")
    title: str = Field(..., description="会话标题")
    created_at: float = Field(..., description="创建时间戳")
    updated_at: float = Field(..., description="更新时间戳")


class AiChatMessageResponse(BaseModel):
    """会话消息响应项"""
    model_config = ConfigDict(from_attributes=True)
    role: str = Field(..., description="角色")
    content: str = Field(..., description="内容")
    reasoning_content: Optional[str] = Field(None, description="推理内容")
    model_id: str = Field("", description="模型ID")
    timestamp: float = Field(0, description="时间戳")
