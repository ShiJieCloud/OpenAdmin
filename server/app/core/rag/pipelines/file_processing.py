from typing import List, Optional

from langchain_core.vectorstores import VectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.core.rag.loaders.loader_registry import LoaderRegistry


class FileProcessingPipeline:
    """
    文件处理流水线

    流程：加载文件 → 切分文档 → 向量化 → 存入向量存储

    支持多格式文件：通过 loader_registry 自动选择对应的加载器
    """

    def __init__(
        self,
        loader_registry: LoaderRegistry,
        splitter: RecursiveCharacterTextSplitter,
        vector_store: VectorStore,
    ):
        self.loader_registry = loader_registry
        self.splitter = splitter
        self.vector_store = vector_store

    def process(
        self,
        file_path: str,
        metadata: Optional[dict] = None,
    ) -> List[str]:
        """
        处理单个文件：加载 → 切分 → 存入向量存储

        Args:
            file_path: 文件绝对路径
            metadata: 业务元数据（kb_id, doc_id 等）

        Returns:
            List[str]: 存入向量存储的文档 ID 列表
        """
        # 1. 根据文件扩展名选择加载器
        loader = self.loader_registry.get(file_path)
        documents = loader.load(file_path=file_path, metadata=metadata)

        # 2. 切分文档
        chunks = self.splitter.split_documents(documents)

        # 3. 存入向量存储
        ids = self.vector_store.add_documents(chunks)

        return ids

    def process_batch(
        self,
        file_paths: List[str],
        metadata: Optional[dict] = None,
    ) -> List[str]:
        """
        批量处理多个文件

        Args:
            file_paths: 文件绝对路径列表
            metadata: 公共业务元数据

        Returns:
            List[str]: 所有存入向量存储的文档 ID 列表
        """
        all_ids: List[str] = []
        for path in file_paths:
            ids = self.process(file_path=path, metadata=metadata)
            all_ids.extend(ids)
        return all_ids
