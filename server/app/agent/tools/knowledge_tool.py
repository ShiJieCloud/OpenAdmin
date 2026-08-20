"""
知识库检索工具模块

基于 RAG 向量检索，为 Agent 提供知识库问答能力
采用延迟初始化模式，避免模块导入时创建检索器和处理文件
"""

from functools import lru_cache
from langchain_core.tools import BaseTool, create_retriever_tool

from app.core.logger import logger


@lru_cache()
def get_knowledge_tool() -> BaseTool:
    """延迟获取知识库工具（单例模式）

    Returns:
        BaseTool: 配置好的知识库检索工具

    Note:
        首次调用时才会初始化检索器
    """
    try:
        from app.core.rag.rag_factory import rag_factory

        retriever = rag_factory.get_retriever()

        tool = create_retriever_tool(
            retriever=retriever,
            name="knowledge_tool",
            description=(
                "查询OpenAdmin系统内部知识库工具。"
                "当用户提问涉及OpenAdmin功能说明、使用方法、配置、业务规则、系统文档相关问题时，请调用本工具获取参考文档片段。"
                "⚠️不要调用本工具处理常识问题、通用知识、简单计算、无需查阅内部文档的问题。"
                "工具返回相关文档片段以及文档来源source，回答问题优先以知识库返回内容为准。"
            )
        )

        logger.info("知识库工具初始化成功")
        return tool
    except Exception as e:
        logger.error(f"知识库工具初始化失败: {e}")
        raise

