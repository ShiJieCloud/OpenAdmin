from __future__ import annotations

from typing import List, Optional

from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document

from .base_loader import BaseLoader


class TxtLoader(BaseLoader):
    """
    纯文本文件加载器

    优先使用utf‑8解码，遇到Windows生成GBK编码文件自动降级兼容。
    支持 .txt / .log 文本类文件
    """

    def load(
        self,
        file_path: str,
        encoding: str = "utf-8",
        metadata: Optional[dict] = None,
    ) -> List[Document]:
        try:
            raw_loader = TextLoader(file_path, encoding=encoding)
            docs = raw_loader.load()
        except Exception as e:
            print(f"加载文件 {file_path} 失败: {e}")
            raise e

        if metadata is not None:
            for doc in docs:
                doc.metadata.update(metadata)
        return docs
