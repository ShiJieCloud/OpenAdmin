"""
Qwen 模型客户端适配器

本模块提供阿里云 Qwen 系列模型的 LangChain 客户端实现，
通过重写流式响应处理逻辑，支持提取模型的推理过程（reasoning_content）。

主要功能：
- 继承 LangChain ChatOpenAI 客户端
- 重写 chunk 转换方法，提取 Qwen 特有的 reasoning_content 字段
- 将推理内容注入到消息的 additional_kwargs 中，供上层应用使用

@since 2026-08-19
@version 1.0.0
@author OpenAdmin Team
"""

from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessageChunk
from langchain_core.outputs import ChatGenerationChunk


class QwenChatOpenAI(ChatOpenAI):
    """
    阿里云 Qwen 模型客户端
    
    继承自 LangChain 的 ChatOpenAI，专门用于处理 Qwen 系列模型的流式响应。
    通过重写 _convert_chunk_to_generation_chunk 方法，提取 Qwen 模型特有的
    reasoning_content 字段（推理过程），并将其注入到消息的 additional_kwargs 中。
    
    使用场景：
    - 需要展示模型推理过程的对话场景
    - 需要区分"思考过程"和"最终回答"的 Agent 应用
    - 需要完整获取 Qwen3 系列模型输出的应用
    
    注意事项：
    - 必须在初始化时设置 extra_body={"enable_thinking": True} 以启用推理
    - reasoning_content 会存储在 AIMessageChunk.additional_kwargs["reasoning_content"]
    - 兼容 LangChain Agent 的 stream_mode="messages" 流式输出模式
    
    Attributes:
        继承自 ChatOpenAI 的所有属性
    
    Example:
        ```python
        llm = QwenChatOpenAI(
            model="qwen3.8-max",
            api_key="sk-xxx",
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            streaming=True,
            extra_body={"enable_thinking": True}
        )
        
        # 流式调用
        async for chunk, metadata in llm.astream(messages, stream_mode="messages"):
            if isinstance(chunk, AIMessageChunk):
                reasoning = chunk.additional_kwargs.get("reasoning_content")
                if reasoning:
                    print(f"[推理] {reasoning}")
                if chunk.content:
                    print(f"[回答] {chunk.content}")
        ```
    """
    
    def _convert_chunk_to_generation_chunk(
        self,
        chunk: dict,
        default_chunk_class: type,
        base_generation_info: dict | None,
    ) -> ChatGenerationChunk | None:
        """
        重写流式 chunk 转换方法，提取 Qwen 的 reasoning_content
        
        本方法在 LangChain 标准的 chunk 处理流程基础上，增加了对 Qwen 模型
        特有的 reasoning_content 字段的提取逻辑。推理内容会被注入到生成的
        ChatGenerationChunk 的 additional_kwargs 中。
        
        处理流程：
        1. 调用父类方法生成标准的 ChatGenerationChunk
        2. 从原始 chunk 中提取 choices[0].delta.reasoning_content
        3. 如果存在推理内容，将其注入到 message.additional_kwargs
        
        Args:
            chunk: 原始流式响应 chunk，包含 choices、usage 等字段
            default_chunk_class: 默认的消息 chunk 类（AIMessageChunk 或其他）
            base_generation_info: 基础生成信息，包含模型元数据等
        
        Returns:
            ChatGenerationChunk | None: 转换后的生成 chunk，如果原始 chunk
            无效则返回 None
        
        Note:
            - Qwen3 系列模型在 enable_thinking=True 时会返回 reasoning_content
            - reasoning_content 表示模型的推理/思考过程
            - 推理内容和最终回答会分别存储在不同的字段中
        
        See Also:
            - LangChain ChatOpenAI._convert_chunk_to_generation_chunk
            - Qwen API 文档：https://help.aliyun.com/zh/model-studio/
        """
        # 步骤 1: 调用父类方法生成标准的 ChatGenerationChunk
        # 父类会处理 content、tool_calls、usage 等标准字段
        generation_chunk = super()._convert_chunk_to_generation_chunk(
            chunk, default_chunk_class, base_generation_info
        )
        
        # 如果父类返回 None，说明 chunk 无效，直接返回
        if generation_chunk is None:
            return None

        # 步骤 2: 从原始 chunk 中提取 Qwen 特有的 reasoning_content
        # Qwen 的流式响应结构：{"choices": [{"delta": {"reasoning_content": "..."}}]}
        choices = chunk.get("choices", [])
        if not choices:
            return generation_chunk
        
        choice = choices[0]
        delta = choice.get("delta", {})
        
        # 步骤 3: 提取并注入 reasoning_content
        reasoning_content = delta.get("reasoning_content")
        if reasoning_content and isinstance(generation_chunk.message, AIMessageChunk):
            # 将推理内容注入到 additional_kwargs，供上层应用读取
            # 使用方式：chunk.additional_kwargs.get("reasoning_content")
            generation_chunk.message.additional_kwargs["reasoning_content"] = reasoning_content
        
        return generation_chunk
