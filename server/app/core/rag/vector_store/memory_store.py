from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.embeddings import Embeddings
from typing import Optional


def create_memory_vector_store(
    embeddings: Optional[Embeddings] = None,
) -> InMemoryVectorStore:
    """
    创建基于内存的向量存储

    Args:
        embeddings: 嵌入模型实例，如果为 None 则需要后续手动添加文档时指定

    Returns:
        InMemoryVectorStore: 内存向量存储实例
    """
    if embeddings is not None:
        vector_store = InMemoryVectorStore(embeddings)
    else:
        vector_store = InMemoryVectorStore()

    return vector_store
