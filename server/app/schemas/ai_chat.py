from pydantic import BaseModel, Field
from typing import Literal


class ChatMessage(BaseModel):
    """聊天消息"""
    role: Literal["user", "assistant", "system"] = Field(..., description="消息角色：user=用户, assistant=助手, system=系统")
    content: str = Field(..., description="消息内容", min_length=1)


class AiChatRequest(BaseModel):
    """AI 对话请求"""
    model: str = Field(..., description="模型标识（需在 LLM_MODELS 配置中）", example="qwen3.7-plus")
    messages: list[ChatMessage] = Field(..., description="对话消息列表", min_length=1)


class ChatResponse(BaseModel):
    """AI 对话响应（非流式）"""
    content: str = Field(..., description="AI 回复内容")
    model: str = Field(..., description="使用的模型名称")
    usage: dict | None = Field(None, description="Token 使用统计")


class StreamChatChunk(BaseModel):
    """流式对话单个数据块"""
    content: str = Field(..., description="增量内容")
    model: str = Field(..., description="模型名称")
    finish_reason: str | None = Field(None, description="结束原因：stop=正常结束, length=达到长度限制")
