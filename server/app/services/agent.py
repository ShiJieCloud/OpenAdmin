"""
Agent 对话服务模块

提供统一的 Agent 对话流式接口，封装：
- LLM 实例创建（通过 LLMFactory）
- 工具组装（通过 ToolFactory）
- Agent 调用（通过 ChatAgent）
- 事件流式输出（AgentEvent）
- 会话记忆（通过 Redis Checkpointer，按 session_id 隔离）

@since 2026-08-20
@version 3.0.0
"""

from typing import AsyncGenerator, Optional

from langgraph.checkpoint.base import BaseCheckpointSaver

from app.core.llm import LLMFactory
from app.agent.agents import ChatAgent
from app.agent.agents.chat_agent import AgentEvent
from app.agent.tools import ToolFactory
from app.agent.prompts import PromptBuilder
from app.agent.checkpointers.redis_checkpointer import RedisCheckpointer
from app.core.logger import logger
from langchain_core.messages import HumanMessage


class AgentService:
    """
    Agent 对话服务

    统一的流式对话接口，支持：
    - 多模型切换（通过 model_id）
    - 工具自动组装（Service 内部决策）
    - 事件分类输出（content / reasoning / tool_call / tool_result）
    - Jinja2 模板提示词（动态注入工具列表、用户信息等）
    - 会话记忆（Redis Checkpointer，按 session_id 隔离，持久化）

    记忆策略：
    - Redis Checkpointer 单例，所有会话共享，按 session_id 隔离
    - session_id 必填：前端首轮通过 POST /ai/chat/session 获取
    - 前端每轮只需传本轮新消息，历史由 checkpointer 自动加载/持久化
    - 不要重传全量历史，否则会与 checkpointer 中的历史重复
    """

    def __init__(self):
        self._prompt_builder = PromptBuilder()
        self._checkpointer: Optional[BaseCheckpointSaver] = None

    async def _get_checkpointer(self) -> BaseCheckpointSaver:
        """
        获取 Redis Checkpointer（延迟初始化）

        Returns:
            AsyncRedisSaver 实例
        """
        if self._checkpointer is None:
            self._checkpointer = await RedisCheckpointer.get_instance()
            logger.info("Redis Checkpointer 初始化完成")
        return self._checkpointer

    async def chat_stream(
        self,
        model_id: str,
        message: HumanMessage,
        session_id: str,
        system_prompt: str | None = None,
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        统一流式对话接口

        Args:
            model_id: 模型标识（需在 LLM_MODELS 配置中）
            message: 本轮新消息，格式为 HumanMessage
                历史由 checkpointer 按 session_id 自动加载，无需重传全量历史。
            session_id: 会话标识（必填）。
                用于隔离不同会话状态；agent 自动读取/写入该会话的历史。
                首轮通过 POST /ai/chat/session 获取。
            system_prompt: 系统提示词（可选，默认使用内置提示词）

        Yields:
            AgentEvent: 分类后的事件对象
                - type="content": 回答内容
                - type="reasoning": 推理过程
                - type="tool_call": 工具调用请求
                - type="tool_result": 工具执行结果
        """
        try:
            # 1. 获取 Redis Checkpointer
            checkpointer = await self._get_checkpointer()

            # 2. 创建 LLM 实例
            llm = LLMFactory.create(model_id)
            logger.info(f"创建 LLM 实例: {model_id} | session: {session_id}")

            # 3. 创建工具集（Service 内部决策）
            tools = ToolFactory.create_all_tools(llm)
            logger.info(f"创建工具集, 工具数: {len(tools)}")

            # 4. 确定系统提示词
            if system_prompt is None:
                # 使用 Jinja2 模板渲染提示词
                system_prompt = self._prompt_builder.render(
                    "chat_agent",
                    app_name="OpenAdmin",
                    tools=tools,
                    user=None,  # TODO: 从请求上下文获取用户信息
                )
                logger.debug(f"渲染系统提示词: {len(system_prompt)} 字符")

            # 5. 创建 Agent（注入 Redis checkpointer）
            agent = ChatAgent(
                llm_client=llm,
                system_prompt=system_prompt,
                tools=tools,
                checkpointer=checkpointer,
            )

            # 6. 流式输出（包含工具事件，透传 session_id 启用记忆）
            #    message 为 HumanMessage 格式，LangGraph 的 add_messages reducer 会自动转换为 BaseMessage
            async for event in agent.astream(
                message,
                session_id=session_id,
                include_tool_events=True,
            ):
                yield event

        except Exception as e:
            logger.error(f"流式对话失败: {e}")
            raise
