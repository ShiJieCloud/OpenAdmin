from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    """聊天消息"""
    content: str = Field(..., description="消息内容")


class AiChatRequest(BaseModel):
    """AI 对话请求"""
    model: str = Field(..., description="模型标识", example="qwen3.7-plus")
    message: ChatMessage = Field(..., description="消息内容")
    session_id: str = Field(..., description="会话 ID", example="a1b2c3d4e5f6...")
