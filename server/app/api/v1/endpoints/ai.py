"""
AI 对话 API 模块

提供模型列表查询、会话 CRUD 和流式对话接口

@since 2026-08-20
@version 3.0.0
"""

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from langchain_core.messages import HumanMessage
import uuid

from app.deps.service import get_agent_service, get_ai_session_service
from app.schemas.ai_chat import AiChatRequest
from app.schemas.ai_session import AiChatSessionResponse, AiChatMessageResponse
from app.services import AgentService
from app.services.ai_session import AiSessionService
from app.agent.checkpointers.redis_checkpointer import RedisCheckpointer
from app.core.logger import logger
from app.config.llm import llm_config
import json
from app.schemas.base.response import ApiResponse
from app.core.response import ResponseBuilder
from app.deps import get_current_active_user


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
    "/chat/session",
    response_model=ApiResponse[str],
    summary="创建会话",
    description="生成新的会话 ID 并在 Redis 中注册。前端首轮调用获取 session_id，后续对话轮回传该值。"
)
async def create_chat_session(
    current_user = Depends(get_current_active_user),
    ai_session_service: AiSessionService = Depends(get_ai_session_service)
):
    """
    创建会话接口

    生成一个新的会话 ID（32 位十六进制，无连字符），
    并在 Redis 中注册该会话的元数据。
    前端在发起流式对话前应先调用本接口获取 session_id，
    之后每轮对话只需传本轮新消息 + session_id，历史由后端自动维护。

    :return: 会话 ID
    """
    logger.info(f"创建会话 | user_id: {current_user.id}")
    session_id = uuid.uuid4().hex
    await ai_session_service.create_session(
        session_id=session_id,
        user_id=current_user.id,
    )
    logger.info(f"创建会话 | session_id: {session_id} | user_id: {current_user.id}")
    return ResponseBuilder.success(data=session_id)


@router.get(
    "/chat/sessions",
    response_model=ApiResponse[list[AiChatSessionResponse]],
    summary="获取用户会话列表",
    description="获取指定用户的所有会话列表，按更新时间倒序排列。"
)
async def list_sessions(
    current_user = Depends(get_current_active_user),
    limit: int = Query(default=100, ge=1, le=500, description="返回数量上限"),
    ai_session_service: AiSessionService = Depends(get_ai_session_service),
):
    """
    获取用户会话列表

    :param user_id: 用户 ID
    :param limit: 返回数量上限
    :return: 会话列表 [{ session_id, title, created_at, updated_at }]
    """
    sessions = await ai_session_service.list_user_sessions(user_id=current_user.id, limit=limit)
    return ResponseBuilder.success(data=sessions)


@router.get(
    "/chat/sessions/{session_id}/messages",
    response_model=ApiResponse[list[AiChatMessageResponse]],
    summary="获取会话消息历史",
    description="获取指定会话的消息历史，按时间顺序排列。"
)
async def get_session_messages(
    session_id: str,
    limit: int = Query(default=200, ge=1, le=1000, description="返回数量上限"),
    ai_session_service: AiSessionService = Depends(get_ai_session_service),
):
    """
    获取会话消息历史

    :param session_id: 会话 ID
    :param limit: 返回数量上限
    :return: 消息列表 [{ role, content, reasoning_content, model_id, timestamp }]
    """
    messages = await ai_session_service.get_messages(session_id=session_id, limit=limit)
    return ResponseBuilder.success(data=messages)


@router.delete(
    "/chat/sessions/{session_id}",
    response_model=ApiResponse[bool],
    summary="删除会话",
    description="删除指定会话及其所有消息数据。"
)
async def delete_session(
    session_id: str,
    current_user = Depends(get_current_active_user),
    ai_session_service: AiSessionService = Depends(get_ai_session_service),
):
    """
    删除会话接口

    删除指定会话及其所有消息数据，同时从用户会话列表中移除，
    并联动清理 LangGraph Agent 的 checkpoint 记忆数据。

    :param session_id: 会话 ID
    :param current_user: 当前活跃用户
    :return: 删除结果
    """
    meta = await ai_session_service.get_session(session_id)
    if meta is None or meta.user_id != current_user.id:
        return ResponseBuilder.error(message="会话不存在或无权限", code=404)

    await ai_session_service.delete_session(session_id=session_id, user_id=current_user.id)
    # 联动清理 Agent checkpoint 记忆数据（session_id 即 thread_id）
    await RedisCheckpointer.delete_thread(session_id)
    logger.info(f"删除会话 | session_id: {session_id} | user_id: {current_user.id}")
    return ResponseBuilder.success(data=True)


@router.post(
    "/chat/stream",
    summary="AI 对话（流式）",
    description="发送消息给 AI，以流式方式返回响应。适用于长文本生成场景，实时显示生成内容。"
)
async def chat_stream(
    request: AiChatRequest,
    current_user = Depends(get_current_active_user),
    agent_service: AgentService = Depends(get_agent_service),
    ai_session_service: AiSessionService = Depends(get_ai_session_service),
):
    """
    AI 对话接口（流式）

    接收用户本轮新消息，以 Server-Sent Events (SSE) 格式流式返回 AI 响应。
    支持多种事件类型：content（内容）、reasoning（推理）、tool_call（工具调用）、tool_result（工具结果）。

    :param request: 对话请求，包含模型标识、本轮新消息、会话 ID
    :param current_user: 当前活跃用户（用于消息持久化）
    :return: 流式响应，SSE 格式
    """

    async def stream_generator():
        """生成 SSE 格式的流式响应"""
        # 累积本轮 AI 回复内容，用于流结束后持久化
        ai_response_content = ""
        ai_reasoning = ""
        try:
            async for event in agent_service.chat_stream(
                model_id=request.model,
                message=HumanMessage(content=request.message.content),
                session_id=request.session_id,
            ):
                # 根据事件类型构建不同的 payload
                if event.type == "content":
                    content = event.data.content
                    if content:
                        ai_response_content += content
                        payload = json.dumps({
                            "type": "content",
                            "content": content
                        }, ensure_ascii=False)
                        yield f"data: {payload}\n\n"

                elif event.type == "reasoning":
                    reasoning = event.data.additional_kwargs.get("reasoning_content", "")
                    if reasoning:
                        ai_reasoning += reasoning
                        payload = json.dumps({
                            "type": "reasoning",
                            "reasoning": reasoning
                        }, ensure_ascii=False)
                        yield f"data: {payload}\n\n"

                elif event.type == "tool_call":
                    tool_calls = event.data.tool_calls
                    if tool_calls:
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

            # 流式完成后持久化本轮消息
            await ai_session_service.save_round_messages(
                session_id=request.session_id,
                model_id=request.model,
                user_message=request.message.content,
                ai_response=ai_response_content,
                ai_reasoning=ai_reasoning,
            )

        except Exception as e:
            logger.error(f"流式响应生成失败: {e}")
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
