from langchain_core.vectorstores import VectorStore, VectorStoreRetriever
from typing import Optional


def create_retriever(
    vector_store: VectorStore,
    search_type: str = "similarity",
    k: int = 4,
) -> VectorStoreRetriever:
    """
    从向量存储创建检索器

    Args:
        vector_store: 向量存储实例
        search_type: 检索类型，支持 "similarity"、"mmr"、"similarity_score_threshold"
        k: 返回的文档数量

    Returns:
        VectorStoreRetriever: 向量检索器实例
    """
    search_kwargs = {"k": k}

    retriever = vector_store.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs,
    )

    return retriever
