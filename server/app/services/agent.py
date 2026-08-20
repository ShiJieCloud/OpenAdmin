"""
Agent 对话服务模块

提供统一的 Agent 对话流式接口，封装：
- LLM 实例创建（通过 LLMFactory）
- 工具组装（通过 ToolFactory）
- Agent 调用（通过 ChatAgent）
- 事件流式输出（AgentEvent）

@since 2026-08-20
@version 2.0.0
"""

from typing import AsyncGenerator
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage

from app.core.llm import LLMFactory
from app.agent.agents import ChatAgent
from app.agent.agents.chat_agent import AgentEvent
from app.agent.tools import ToolFactory
from app.agent.prompts import PromptBuilder
from app.core.logger import logger


class AgentService:
    """
    Agent 对话服务

    统一的流式对话接口，支持：
    - 多模型切换（通过 model_id）
    - 工具自动组装（Service 内部决策）
    - 事件分类输出（content / reasoning / tool_call / tool_result）
    - Jinja2 模板提示词（动态注入工具列表、用户信息等）

    Example:
        ```python
        service = AgentService()
        async for event in service.chat_stream("qwen3-max", messages):
            if event.type == "content":
                print(event.data.content)
        ```
    """

    def __init__(self):
        self._prompt_builder = PromptBuilder()

    @staticmethod
    def _build_messages(messages: list[dict]) -> list[BaseMessage]:
        """
        构建 LangChain 消息格式

        Args:
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]

        Returns:
            list[BaseMessage]: LangChain 消息对象列表
        """
        langchain_messages = []
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")

            if role == "user":
                langchain_messages.append(HumanMessage(content=content))
            elif role == "assistant":
                langchain_messages.append(AIMessage(content=content))
            elif role == "system":
                langchain_messages.append(SystemMessage(content=content))

        return langchain_messages

    async def chat_stream(
        self,
        model_id: str,
        messages: list[dict],
        system_prompt: str | None = None,
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        统一流式对话接口

        Args:
            model_id: 模型标识（需在 LLM_MODELS 配置中）
            messages: 消息列表，格式为 [{"role": "user", "content": "..."}]
            system_prompt: 系统提示词（可选，默认使用内置提示词）

        Yields:
            AgentEvent: 分类后的事件对象
                - type="content": 回答内容
                - type="reasoning": 推理过程
                - type="tool_call": 工具调用请求
                - type="tool_result": 工具执行结果
        """
        try:
            # 1. 创建 LLM 实例
            llm = LLMFactory.create(model_id)
            logger.info(f"创建 LLM 实例: {model_id}")

            # 2. 创建工具集（Service 内部决策）
            tools = ToolFactory.create_all_tools(llm)
            logger.info(f"创建工具集, 工具数: {len(tools)}")

            # 3. 确定系统提示词
            if system_prompt is None:
                # 使用 Jinja2 模板渲染提示词
                system_prompt = self._prompt_builder.render(
                    "chat_agent",
                    app_name="OpenAdmin",
                    tools=tools,
                    user=None,  # TODO: 从请求上下文获取用户信息
                )
                logger.debug(f"渲染系统提示词: {len(system_prompt)} 字符")

            # 4. 创建 Agent
            agent = ChatAgent(
                llm_client=llm,
                system_prompt=system_prompt,
                tools=tools,
            )

            # 5. 构建消息
            langchain_messages = self._build_messages(messages)

            # 6. 流式输出（包含工具事件）
            async for event in agent.astream(langchain_messages, include_tool_events=True):
                yield event

        except Exception as e:
            logger.error(f"流式对话失败: {e}")
            raise