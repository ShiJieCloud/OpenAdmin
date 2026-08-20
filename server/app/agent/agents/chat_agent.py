"""
聊天智能体模块

基于 LangChain create_react_agent 构建，提供：
- 流式输出（stream_mode="messages"）
- 推理过程提取（reasoning_content → additional_kwargs）
- 工具调用事件暴露（tool_call / tool_result）
- 事件分类（content / reasoning / tool_call / tool_result）

典型用法：
    ```python
    from app.agent.agents.chat_agent import ChatAgent
    from app.core.llm import LLMFactory

    llm = LLMFactory.create("qwen3-max")
    agent = ChatAgent(llm, "你是数据库助手")

    # 仅输出 content/reasoning
    async for event in agent.astream(messages):
        if event.type == "content":
            print(event.data.content)

    # 包含工具调用事件
    async for event in agent.astream(messages, include_tool_events=True):
        if event.type == "tool_call":
            print(f"调用工具: {event.data.tool_calls}")
        elif event.type == "tool_result":
            print(f"工具结果: {event.data.content}")
    ```

@since 2026-08-19
@version 2.2.0
"""

from typing import AsyncGenerator, Literal
from langchain.agents import create_agent
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, AIMessageChunk, ToolMessage
from langchain_core.tools import BaseTool


# 事件类型定义
EventType = Literal["content", "reasoning", "tool_call", "tool_result"]


class AgentEvent:
    """
    Agent 流式事件

    Attributes:
        type: 事件类型（content/reasoning/tool_call/tool_result）
        data: 事件数据（AIMessageChunk 或 ToolMessage）
    """

    def __init__(self, type: EventType, data: BaseMessage):
        self.type = type
        self.data = data

    def __repr__(self):
        return f"AgentEvent(type={self.type!r}, data={self.data!r})"


class ChatAgent:
    """
    聊天智能体

    封装 LangChain ReAct Agent，提供流式对话能力。
    支持推理过程（reasoning_content）和回答内容（content）的分离提取。

    Attributes:
        _agent: LangChain CompiledStateGraph 实例

    Example:
        ```python
        # 简单用法
        agent = ChatAgent(llm, system_prompt)

        # 带工具用法
        agent = ChatAgent(llm, system_prompt, tools=[sql_tool, search_tool])

        # 自定义 SystemMessage
        agent = ChatAgent(llm, SystemMessage(content="你是{role}助手"))
        ```
    """

    def __init__(
        self,
        llm_client: BaseChatModel,
        system_prompt: str | SystemMessage,
        tools: list[BaseTool] | None = None,
    ):
        """
        初始化聊天智能体

        Args:
            llm_client: LLM 客户端实例
            system_prompt: 系统提示词（str 或 SystemMessage）
            tools: 工具列表（可选）
        """
        # 延迟初始化参数
        self._agent = None
        self._init_params = {
            'llm_client': llm_client,
            'tools': tools,
            'system_prompt': system_prompt,
        }

    async def _ensure_agent(self):
        """确保 agent 已初始化（延迟初始化）"""
        if self._agent is None:
            self._agent = create_agent(
                model=self._init_params['llm_client'],
                tools=self._init_params['tools'],
                system_prompt=self._init_params['system_prompt'],
            )

    async def astream(
        self,
        messages: list[BaseMessage],
        *,
        include_tool_events: bool = False
    ) -> AsyncGenerator[AgentEvent, None]:
        """
        流式输出对话结果

        Args:
            messages: 消息列表
            include_tool_events: 是否包含工具调用事件（默认 False，仅输出 content/reasoning）

        Yields:
            AgentEvent: 分类后的事件对象
                - type="content": 回答内容（AIMessageChunk）
                - type="reasoning": 推理过程（AIMessageChunk）
                - type="tool_call": 工具调用请求（AIMessageChunk with tool_calls）
                - type="tool_result": 工具执行结果（ToolMessage）

        Note:
            推理过程提取需要 LLM 启用推理模式（enable_thinking=True）
        """
        # 确保 agent 已初始化
        await self._ensure_agent()
        
        # 获取流式迭代器
        async for chunk, _metadata in self._agent.astream(
            {"messages": messages},
            stream_mode="messages"
        ):
            # 处理 ToolMessage（工具执行结果）
            if isinstance(chunk, ToolMessage):
                if include_tool_events:
                    yield AgentEvent(type="tool_result", data=chunk)
                continue

            # 只处理 AIMessageChunk
            if not isinstance(chunk, AIMessageChunk):
                continue

            # 分类事件
            has_content = bool(chunk.content)
            has_reasoning = bool(chunk.additional_kwargs.get("reasoning_content"))
            has_tool_calls = bool(chunk.tool_calls)

            # 工具调用请求
            if has_tool_calls and include_tool_events:
                yield AgentEvent(type="tool_call", data=chunk)

            # 推理过程
            if has_reasoning:
                yield AgentEvent(type="reasoning", data=chunk)

            # 回答内容
            if has_content:
                yield AgentEvent(type="content", data=chunk)
