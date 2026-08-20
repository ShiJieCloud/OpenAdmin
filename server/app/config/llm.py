"""
LLM 配置模块

提供大语言模型的配置管理，采用**平台凭证共享 + 模型参数独立**的架构。

配置结构：
- 平台级凭证：API_KEY、BASE_URL（所有模型共享）
- 模型级参数：model_name、temperature、max_tokens 等（每个模型独立配置）

典型用法：
    ```python
    from app.config import llm_config
    
    # 获取平台凭证
    api_key = llm_config.API_KEY
    base_url = llm_config.BASE_URL
    
    # 获取模型配置
    model_config = llm_config.get_model_config("qwen3-max")
    temperature = model_config.temperature
    ```

@since 2026-08-19
@version 2.0.0
"""

from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict
from pydantic import Field, BaseModel


class ModelConfig(BaseModel):
    """
    单个模型的配置（仅模型级别参数）
    
    本配置类只包含模型级别的参数，平台级凭证（API_KEY、BASE_URL）
    由 LLMConfig 统一管理，所有模型共享。
    
    Attributes:
        model_name: 模型名称（如 qwen3-max、qwen3.8-max）
        temperature: 采样温度，范围 0-2，默认 0.7
        max_tokens: 最大生成 token 数，None 表示不限制
        timeout: 请求超时时间（秒），默认 60
        enable_thinking: 是否启用推理模式（Qwen3 系列支持），默认 True
    
    Example:
        ```python
        config = ModelConfig(
            model_name="qwen3-max",
            temperature=0.7,
            max_tokens=2048,
            enable_thinking=True
        )
        ```
    """
    model_name: str = Field(..., description="模型名称（如 qwen3-max、qwen3.8-max）")
    temperature: float = Field(0.7, description="采样温度，范围 0-2")
    max_tokens: int | None = Field(None, description="最大生成 token 数，None 表示不限制")
    timeout: int = Field(60, description="请求超时时间（秒）")
    enable_thinking: bool = Field(True, description="是否启用推理模式（Qwen3 系列支持）")


class LLMConfig(BaseConfig):
    """
    LLM 配置管理类
    
    采用**平台凭证共享 + 模型参数独立**的架构：
    - 平台级凭证（API_KEY、BASE_URL）：所有模型共享，统一管理
    - 模型级参数：每个模型独立配置（temperature、max_tokens 等）
    
    配置来源：
    - 环境变量：LLM_API_KEY、LLM_BASE_URL、LLM_MODELS
    - 配置文件：.env/.env.dev 或 .env/.env.prod
    
    Attributes:
        API_KEY: 平台级 API 密钥（所有模型共享）
        BASE_URL: 平台级 API 基础地址（所有模型共享）
        MODELS: 模型配置字典，key 为模型标识，value 为 ModelConfig
    
    Example:
        ```python
        from app.config import llm_config
        
        # 获取平台凭证
        api_key = llm_config.API_KEY
        base_url = llm_config.BASE_URL
        
        # 获取模型配置
        model_config = llm_config.get_model_config("qwen3-max")
        print(f"模型: {model_config.model_name}")
        print(f"温度: {model_config.temperature}")
        
        # 列出所有可用模型
        models = llm_config.list_models()
        ```
    
    Note:
        - 平台凭证必须在环境变量中配置（LLM_API_KEY、LLM_BASE_URL）
        - 模型配置通过 LLM_MODELS 环境变量以 JSON 格式提供
        - 模型标识（key）用于前端选择和 API 调用，model_name 用于实际请求
    """
    
    # ==================== 平台级凭证（所有模型共享）====================
    API_KEY: str = Field(..., description="平台 API 密钥（所有模型共享）")
    BASE_URL: str = Field(..., description="平台 API 基础地址（所有模型共享）")
    
    # ==================== 模型级配置 ====================
    MODELS: dict[str, ModelConfig] = Field(
        default_factory=dict,
        description="模型配置字典，key 为模型标识，value 为 ModelConfig"
    )

    def get_model_config(self, model_id: str) -> ModelConfig:
        """
        获取指定模型的配置
        
        Args:
            model_id: 模型标识（MODELS 字典的 key，如 "qwen3-max"）
            
        Returns:
            ModelConfig: 该模型的配置对象
            
        Raises:
            KeyError: 模型未配置
            
        Example:
            ```python
            config = llm_config.get_model_config("qwen3-max")
            print(f"模型名称: {config.model_name}")
            print(f"采样温度: {config.temperature}")
            ```
        """
        if model_id not in self.MODELS:
            available = ", ".join(self.MODELS.keys())
            raise KeyError(
                f"模型 [{model_id}] 未配置，当前可用模型: {available}"
            )
        
        return self.MODELS[model_id]

    def list_models(self) -> list[str]:
        """
        列出所有已配置的模型标识
        
        Returns:
            list[str]: 模型标识列表（如 ["qwen3-max", "qwen3.8-max"]）
            
        Example:
            ```python
            models = llm_config.list_models()
            print(f"可用模型: {models}")
            ```
        """
        return list(self.MODELS.keys())

    model_config = SettingsConfigDict(
        env_prefix="LLM_"
    )


llm_config = LLMConfig()
