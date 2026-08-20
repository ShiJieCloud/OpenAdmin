"""
AI 对话 API 模块

提供模型列表查询和流式对话接口

@since 2026-08-20
@version 2.0.0
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse, JSONResponse

from app.deps.service import get_agent_service
from app.schemas.ai_chat import AiChatRequest
from app.services import AgentService
from app.core.logger import logger
from app.config.llm import llm_config
import json
from app.schemas.base.response import ApiResponse
from app.core.response import ResponseBuilder


router = APIRouter()


@router.get(
    "/models",
    response_model=ApiResponse[list[str]],
    summary="获取可用模型列表",
    description="获取系统中已配置的所有可用 AI 模型列表"
)
async def list_models():
    """
    获取可用模型列表接口

    返回系统中已配置的所有 AI 模型标识列表，供前端下拉选择使用。

    :return: 模型标识列表
    """
    models = llm_config.list_models()
    return ResponseBuilder.success(data=models)


@router.post(
    "/chat/stream",
    summary="AI 对话（流式）",
    description="发送消息给 AI，以流式方式返回响应。适用于长文本生成场景，实时显示生成内容。"
)
async def chat_stream(
    request: AiChatRequest,
    agent_service: AgentService = Depends(get_agent_service)
):
    """
    AI 对话接口（流式）

    接收用户消息列表，以 Server-Sent Events (SSE) 格式流式返回 AI 响应。
    支持多种事件类型：content（内容）、reasoning（推理）、tool_call（工具调用）、tool_result（工具结果）。

    :param request: 对话请求，包含模型标识、消息列表、工具组等
    :return: 流式响应，SSE 格式
    """
    logger.info(f"AI 流式对话请求 | model: {request.model}")

    async def stream_generator():
        """生成 SSE 格式的流式响应"""
        try:
            async for event in agent_service.chat_stream(
                model_id=request.model,
                messages=[msg.model_dump() for msg in request.messages],
            ):
                # 根据事件类型构建不同的 payload
                if event.type == "content":
                    content = event.data.content
                    if content:
                        # json.dumps 自动处理换行符转义，无需手动 replace
                        payload = json.dumps({
                            "type": "content",
                            "content": content
                        }, ensure_ascii=False)
                        yield f"data: {payload}\n\n"

                elif event.type == "reasoning":
                    reasoning = event.data.additional_kwargs.get("reasoning_content", "")
                    if reasoning:
                        payload = json.dumps({
                            "type": "reasoning",
                            "reasoning": reasoning
                        }, ensure_ascii=False)
                        yield f"data: {payload}\n\n"

                elif event.type == "tool_call":
                    tool_calls = event.data.tool_calls
                    if tool_calls:
                        # 过滤掉流式过程中 name 为空的中间 chunk
                        valid_tool_calls = [
                            {
                                "name": tc["name"],
                                "args": tc["args"],
                                "id": tc["id"]
                            }
                            for tc in tool_calls
                            if tc.get("name")
                        ]
                        if valid_tool_calls:
                            payload = json.dumps({
                                "type": "tool_call",
                                "tool_calls": valid_tool_calls
                            }, ensure_ascii=False)
                            yield f"data: {payload}\n\n"

                elif event.type == "tool_result":
                    content = event.data.content
                    if content:
                        payload = json.dumps({
                            "type": "tool_result",
                            "tool_call_id": event.data.tool_call_id,
                            "content": content
                        }, ensure_ascii=False)
                        yield f"data: {payload}\n\n"

        except Exception as e:
            logger.error(f"流式响应生成失败: {e}")
            # 发送错误事件
            error_payload = json.dumps({
                "type": "error",
                "message": str(e)
            }, ensure_ascii=False)
            yield f"data: {error_payload}\n\n"

    try:
        return StreamingResponse(
            stream_generator(),
            media_type="text/event-stream",
        )
    except Exception as e:
        logger.error(f"AI 流式对话失败: {e}")
        raise
