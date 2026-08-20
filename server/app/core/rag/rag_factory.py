"""
RAG 组件工厂模块

职责：
- 加载器注册表（按文件扩展名自动选择 Loader）
- 组件缓存（延迟初始化，单例复用）
- 统一入口（pipeline / retriever 一键获取）

设计原则：
- 加载器可插拔：注册新 Loader 即可支持新文件格式
- 组件按需创建：首次访问时初始化，后续复用缓存
- 配置注入：支持外部传入配置，默认使用 rag_config

典型用法：
    ```python
    from app.core.rag.factories import rag_factory

    # 获取检索器（用于 Agent 工具）
    retriever = rag_factory.get_retriever()

    # 获取文件处理流水线（用于文档入库）
    pipeline = rag_factory.get_pipeline()

    # 注册新的加载器（支持 PDF）
    rag_factory.register_loader(".pdf", PdfLoader())
    ```

@since 2026-08-20
@version 2.0.0
"""

from __future__ import annotations

from langchain_core.embeddings import Embeddings
from langchain_core.vectorstores import InMemoryVectorStore, VectorStoreRetriever
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.config.rag import rag_config
from app.core.logger import logger
from app.core.rag.embeddings.embedding_client import create_embedding_client
from app.core.rag.vector_store.memory_store import create_memory_vector_store
from app.core.rag.loaders.base_loader import BaseLoader
from app.core.rag.loaders.txt_loader import TxtLoader
from app.core.rag.loaders.loader_registry import LoaderRegistry
from app.core.rag.pipelines.file_processing import FileProcessingPipeline


class RAGFactory:
    """
    RAG 组件工厂

    统一管理 RAG 各组件的创建和缓存：
    - embedding: 向量化模型
    - vector_store: 向量存储
    - retriever: 检索器
    - splitter: 文档切分器
    - loader_registry: 加载器注册表
    - pipeline: 文件处理流水线

    所有组件延迟初始化，首次访问时创建并缓存。
    """

    def __init__(self):
        # 组件缓存
        self._embedding: Embeddings | None = None
        self._vector_store: InMemoryVectorStore | None = None
        self._retriever: VectorStoreRetriever | None = None
        self._splitter: RecursiveCharacterTextSplitter | None = None
        self._pipeline: FileProcessingPipeline | None = None

        # 加载器注册表
        self._loader_registry = LoaderRegistry()
        self._loader_registry.register(".txt", TxtLoader())
        self._loader_registry.register(".log", TxtLoader())

    # ==================== 加载器管理 ====================

    def register_loader(self, extension: str, loader: BaseLoader) -> None:
        """注册新的文件加载器"""
        self._loader_registry.register(extension, loader)

    def get_loader(self, file_path: str) -> BaseLoader:
        """根据文件路径获取对应的加载器"""
        return self._loader_registry.get(file_path)

    @property
    def supported_extensions(self) -> list[str]:
        """已支持的文件格式列表"""
        return self._loader_registry.supported_extensions()

    # ==================== 核心组件 ====================

    def get_embedding(self) -> Embeddings:
        """获取 Embedding 客户端（缓存）"""
        if self._embedding is None:
            self._embedding = create_embedding_client(
                model=rag_config.EMBEDDING_MODEL,
                api_key=rag_config.EMBEDDING_API_KEY,
                base_url=rag_config.EMBEDDING_BASE_URL,
                dimensions=rag_config.EMBEDDING_DIMENSIONS,
            )
            logger.info("Embedding 客户端创建成功")
        return self._embedding

    def get_vector_store(self) -> InMemoryVectorStore:
        """获取向量存储（缓存）"""
        if self._vector_store is None:
            embedding = self.get_embedding()
            self._vector_store = create_memory_vector_store(embeddings=embedding)
            logger.info("向量存储创建成功")
        return self._vector_store

    def get_retriever(self) -> VectorStoreRetriever:
        """获取检索器（缓存）"""
        if self._retriever is None:
            vector_store = self.get_vector_store()
            search_kwargs: dict = {"k": rag_config.RETRIEVER_K}

            if rag_config.RETRIEVER_SCORE_THRESHOLD is not None:
                search_kwargs["score_threshold"] = rag_config.RETRIEVER_SCORE_THRESHOLD

            self._retriever = vector_store.as_retriever(
                search_type=rag_config.RETRIEVER_SEARCH_TYPE,
                search_kwargs=search_kwargs,
            )
            logger.info(
                f"检索器创建成功 (search_type={rag_config.RETRIEVER_SEARCH_TYPE}, "
                f"k={rag_config.RETRIEVER_K})"
            )
        return self._retriever

    def get_splitter(self) -> RecursiveCharacterTextSplitter:
        """获取文档切分器（缓存）"""
        if self._splitter is None:
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=rag_config.CHUNK_SIZE,
                chunk_overlap=rag_config.CHUNK_OVERLAP,
            )
            logger.info(
                f"文档切分器创建成功 (chunk_size={rag_config.CHUNK_SIZE}, "
                f"overlap={rag_config.CHUNK_OVERLAP})"
            )
        return self._splitter

    # ==================== 流水线 ====================

    def get_pipeline(self) -> FileProcessingPipeline:
        """获取文件处理流水线（缓存）"""
        if self._pipeline is None:
            splitter = self.get_splitter()
            vector_store = self.get_vector_store()
            self._pipeline = FileProcessingPipeline(
                loader_registry=self._loader_registry,
                splitter=splitter,
                vector_store=vector_store,
            )
            logger.info("文件处理流水线创建成功")
        return self._pipeline

    # ==================== 生命周期 ====================

    def reset(self) -> None:
        """重置所有缓存组件（用于测试或重新配置）"""
        self._embedding = None
        self._vector_store = None
        self._retriever = None
        self._splitter = None
        self._pipeline = None
        logger.info("RAG 组件缓存已重置")


rag_factory = RAGFactory()
