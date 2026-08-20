from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from langchain_core.documents import Document


class BaseLoader(ABC):
    """
    所有文档加载器的抽象基类

    所有具体文件解析实现(PDF/TXT/DOCX/Markdown等)都必须继承本类，实现load方法。

    主要职责：
        1. 定义本地文档文件加载的统一接口
        2. 将业务元数据(kb_id、doc_id等)注入每一个Document对象
        3. 提供内置的批量加载能力
        4. 将底层第三方库异常转换为项目领域异常 DocumentParseError

    注意事项：
        ❌禁止直接覆盖 metadata 对象；必须使用 dict.update()
        ✅保证保留解析器自带元数据，例如 page 页码、source 原始来源
    """

    @abstractmethod
    def load(
        self,
        file_path: str,
        metadata: Optional[dict] = None,
    ) -> List[Document]:
        """
        加载单个本地文档文件，返回解析后的Document列表

        Args:
            file_path: 文件的绝对本地路径
            metadata: 业务自定义元字典，会合并到每一个输出Document的metadata中
                常用key：kb_id 知识库ID，doc_id 文档ID，source 文件名，upload_time 上传时间

        Returns:
            List[Document]: langchain标准文档对象数组，包含文本page_content与合并后的元数据metadata

        Raises:
            DocumentParseError: 文件不存在、文件损坏、加密、编码错误、解析失败时抛出
        """
        raise NotImplementedError

    def load_batch(
        self,
        file_paths: List[str],
        base_metadata: Optional[dict] = None,
    ) -> List[Document]:
        """
        顺序批量加载多个文档文件

        默认串行实现；子类可重写本方法实现并发加载，提升大文件批量导入性能。

        ⚠️警告：如果每个文件需要独立不同的 doc_id，不要使用本批量接口！
            请循环调用 load()，为每个文件传入独立metadata。

        Args:
            file_paths: 文件绝对路径列表
            base_metadata: 公共元数据，会应用到这批全部文档上

        Returns:
            List[Document]: 合并全部文件解析后的文档片段

        Raises:
            DocumentParseError: 任意一个文件解析失败，立刻终止并抛出异常
        """
        documents: List[Document] = []
        for path in file_paths:
            try:
                chunk_docs = self.load(file_path=path, metadata=base_metadata)
            except Exception as exc:
                raise Exception(f"批量导入失败，出错文件: [{path}]") from exc
            documents.extend(chunk_docs)
        return documents
