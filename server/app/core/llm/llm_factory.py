"""
LLM 工厂模块

提供 LLM 实例的创建和管理，采用**平台凭证共享 + 模型参数独立**的架构。

主要功能：
- 根据 model_id 创建对应的 LLM 实例
- 实例缓存，避免重复创建
- 提供可用模型列表

典型用法：
    ```python
    from app.core.llm import LLMFactory
    
    # 创建 LLM 实例
    llm = LLMFactory.create("qwen3-max")
    
    # 流式调用
    async for chunk in llm.astream(messages):
        print(chunk.content)
    
    # 获取可用模型列表
    models = LLMFactory.list_models()
    ```

@since 2026-08-19
@version 2.0.0
"""

from app.config import llm_config
from app.core.llm.clients import QwenChatOpenAI


class LLMFactory:
    """
    LLM 实例工厂
    
    负责根据 model_id 创建对应的 LLM 实例，并提供实例缓存机制。
    采用平台凭证共享架构，所有模型使用相同的 API_KEY 和 BASE_URL。
    
    Attributes:
        _cache: 实例缓存字典，key 为 model_id，value 为 LLM 实例
    
    Example:
        ```python
        # 创建 LLM 实例
        llm = LLMFactory.create("qwen3-max")
        
        # 获取可用模型列表
        models = LLMFactory.list_models()
        print(f"可用模型: {models}")
        ```
    
    Note:
        - 实例会被缓存，相同 model_id 多次调用返回同一实例
        - 如需重新创建实例，需清空缓存（_cache.clear()）
    """
    
    _cache: dict[str, QwenChatOpenAI] = {}

    @classmethod
    def create(cls, model_id: str) -> QwenChatOpenAI:
        """
        创建 LLM 实例
        
        根据 model_id 从配置中获取模型参数，使用平台共享凭证创建 LLM 实例。
        实例会被缓存，相同 model_id 多次调用返回同一实例。
        
        Args:
            model_id: 模型标识（如 "qwen3-max"、"qwen3.8-max"）
            
        Returns:
            QwenChatOpenAI: LLM 实例，支持流式输出和推理模式
            
        Raises:
            KeyError: 模型未配置
            
        Example:
            ```python
            # 创建 LLM 实例
            llm = LLMFactory.create("qwen3-max")
            
            # 流式调用
            async for chunk in llm.astream(messages, stream_mode="messages"):
                reasoning = chunk.additional_kwargs.get("reasoning_content")
                content = chunk.content
            ```
        
        Note:
            - 平台凭证（API_KEY、BASE_URL）从 llm_config 获取
            - 模型参数（temperature、max_tokens 等）从 ModelConfig 获取
            - enable_thinking 参数控制是否启用推理模式
        """
        # 检查缓存
        if model_id in cls._cache:
            return cls._cache[model_id]

        # 获取模型配置
        config = llm_config.get_model_config(model_id)

        # 创建 LLM 实例
        instance = QwenChatOpenAI(
            model=config.model_name,
            api_key=llm_config.API_KEY,        # 平台共享凭证
            base_url=llm_config.BASE_URL,      # 平台共享地址
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            request_timeout=config.timeout,    # LangChain 使用 request_timeout
            streaming=True,
            extra_body={"enable_thinking": config.enable_thinking},
        )

        # 缓存实例
        cls._cache[model_id] = instance
        return instance

    @classmethod
    def list_models(cls) -> list[str]:
        """
        获取可用模型列表
        
        Returns:
            list[str]: 模型标识列表（如 ["qwen3-max", "qwen3.8-max"]）
            
        Example:
            ```python
            models = LLMFactory.list_models()
            print(f"可用模型: {models}")
            ```
        """
        return llm_config.list_models()

    @classmethod
    def clear_cache(cls) -> None:
        """
        清空实例缓存
        
        清空后，下次调用 create() 会重新创建实例。
        适用于配置变更后需要重新加载实例的场景。
        
        Example:
            ```python
            # 清空缓存
            LLMFactory.clear_cache()
            
            # 重新创建实例
            llm = LLMFactory.create("qwen3-max")
            ```
        """
        cls._cache.clear()
