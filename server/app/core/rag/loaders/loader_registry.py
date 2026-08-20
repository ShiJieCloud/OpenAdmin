"""
加载器注册表模块

按文件扩展名映射到对应的 Loader 实例。
支持运行时动态注册新格式。

@since 2026-08-20
@version 1.0.0
"""

from __future__ import annotations

from pathlib import Path

from app.core.logger import logger
from app.core.rag.loaders.base_loader import BaseLoader


class LoaderRegistry:
    """
    加载器注册表

    按文件扩展名映射到对应的 Loader 实例。
    支持运行时动态注册新格式。

    Example:
        ```python
        registry = LoaderRegistry()
        registry.register(".txt", TxtLoader())
        loader = registry.get("report.txt")  # -> TxtLoader
        ```
    """

    def __init__(self):
        self._loaders: dict[str, BaseLoader] = {}

    def register(self, extension: str, loader: BaseLoader) -> None:
        """
        注册加载器

        Args:
            extension: 文件扩展名（如 ".txt"、".pdf"）
            loader: 加载器实例
        """
        ext = extension.lower() if extension.startswith(".") else f".{extension.lower()}"
        self._loaders[ext] = loader
        logger.debug(f"注册加载器: {ext} -> {loader.__class__.__name__}")

    def get(self, file_path: str) -> BaseLoader:
        """
        根据文件路径自动选择加载器

        Args:
            file_path: 文件路径

        Returns:
            BaseLoader: 匹配的加载器实例

        Raises:
            ValueError: 没有注册的加载器支持该文件格式
        """
        ext = Path(file_path).suffix.lower()
        loader = self._loaders.get(ext)
        if loader is None:
            supported = ", ".join(sorted(self._loaders.keys()))
            raise ValueError(f"不支持的文件格式: {ext}，已支持: {supported}")
        return loader

    def supported_extensions(self) -> list[str]:
        """返回所有已注册的扩展名"""
        return sorted(self._loaders.keys())
