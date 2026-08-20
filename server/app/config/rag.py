from app.config.base import BaseConfig
from pydantic import Field
from pydantic_settings import SettingsConfigDict


class RAGConfig(BaseConfig):
    """RAG 相关配置"""

    # ==================== Embedding 配置 ====================
    EMBEDDING_API_KEY: str = Field(..., description="Embedding 模型的 API 密钥")
    EMBEDDING_BASE_URL: str = Field(..., description="Embedding 模型的 API 基础地址")
    EMBEDDING_MODEL: str = Field(default="text-embedding-3", description="Embedding 模型名称")
    EMBEDDING_DIMENSIONS: int = Field(default=1536, description="向量维度")

    # ==================== 文档切分配置 ====================
    CHUNK_SIZE: int = Field(default=1024, description="文档切分块大小")
    CHUNK_OVERLAP: int = Field(default=128, description="切分重叠大小")

    # ==================== 检索配置 ====================
    RETRIEVER_SEARCH_TYPE: str = Field(default="similarity", description="检索类型: similarity/mmr/similarity_score_threshold")
    RETRIEVER_K: int = Field(default=4, description="返回文档数量")
    RETRIEVER_SCORE_THRESHOLD: float | None = Field(default=None, description="相似度阈值")

    model_config = SettingsConfigDict(
        env_prefix="RAG_"
    )


rag_config = RAGConfig()
