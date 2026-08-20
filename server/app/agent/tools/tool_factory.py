"""
工具工厂模块

统一管理 Agent 工具的创建和组合，提供：
- 全量工具集（SQL + 搜索 + 知识库）
- 按功能分组的工具集（SQL / RAG）
- 延迟初始化，避免启动时副作用

典型用法：
    ```python
    from app.agent.tools.factory import ToolFactory
    
    # 创建所有工具
    tools = ToolFactory.create_all_tools(llm)
    
    # 仅创建 SQL 工具
    sql_tools = ToolFactory.create_sql_tools(llm)
    
    # 仅创建 RAG 工具
    rag_tools = ToolFactory.create_rag_tools()
    ```

@since 2026-08-20
@version 1.0.0
"""

from typing import Literal
from langchain_core.tools import BaseTool
from langchain_core.language_models import BaseLanguageModel

from app.core.logger import logger


class ToolFactory:
    """
    工具工厂
    
    统一管理工具创建，支持按需组合和延迟初始化。
    所有工具方法都是静态方法，无需实例化。
    
    Example:
        ```python
        # 创建所有工具
        tools = ToolFactory.create_all_tools(llm)
        
        # 创建特定工具组
        sql_tools = ToolFactory.create_sql_tools(llm)
        rag_tools = ToolFactory.create_rag_tools()
        ```
    """
    
    @staticmethod
    def create_sql_tools(llm: BaseLanguageModel) -> list[BaseTool]:
        """
        创建 SQL 数据库工具
        
        Args:
            llm: LLM 实例（用于 SQL 工具理解数据库结构）
            
        Returns:
            list[BaseTool]: SQL 工具列表，包含：
                - query_sql_database: 执行 SQL 查询
                - list_sql_tables: 列出所有表
                - get_table_schema: 获取表结构
                - get_table_description: 获取表描述
                
        Note:
            首次调用时初始化数据库连接
        """
        from .db_tool import sql_toolkit
        
        tools = sql_toolkit(llm)
        logger.info(f"创建 SQL 工具: {[t.name for t in tools]}")
        return tools
    
    @staticmethod
    def create_rag_tools() -> list[BaseTool]:
        """
        创建 RAG 工具（搜索 + 知识库）
        
        Returns:
            list[BaseTool]: RAG 工具列表，包含：
                - search_tool: 网络搜索
                - knowledge_tool: 知识库检索
                
        Note:
            首次调用时初始化搜索客户端和向量检索器
        """
        from .search_tool import get_search_tool
        from .knowledge_tool import get_knowledge_tool
        
        tools = [get_search_tool(), get_knowledge_tool()]
        logger.info(f"创建 RAG 工具: {[t.name for t in tools]}")
        return tools
    
    @staticmethod
    def create_all_tools(llm: BaseLanguageModel) -> list[BaseTool]:
        """
        创建所有工具（SQL + RAG）
        
        Args:
            llm: LLM 实例
            
        Returns:
            list[BaseTool]: 完整工具列表
            
        Example:
            ```python
            tools = ToolFactory.create_all_tools(llm)
            agent = ChatAgent(llm, system_prompt, tools=tools)
            ```
        """
        sql_tools = ToolFactory.create_sql_tools(llm)
        rag_tools = ToolFactory.create_rag_tools()
        
        all_tools = sql_tools + rag_tools
        logger.info(f"创建完整工具集: {[t.name for t in all_tools]}")
        return all_tools
    
    @staticmethod
    def create_tools(
        llm: BaseLanguageModel,
        tool_groups: list[Literal["sql", "rag", "all"]] | None = None
    ) -> list[BaseTool]:
        """
        按工具组创建工具
        
        Args:
            llm: LLM 实例
            tool_groups: 工具组列表，可选值：
                - "sql": SQL 数据库工具
                - "rag": RAG 工具（搜索 + 知识库）
                - "all": 所有工具（默认）
                
        Returns:
            list[BaseTool]: 组合后的工具列表
            
        Example:
            ```python
            # 仅使用 SQL 工具
            tools = ToolFactory.create_tools(llm, ["sql"])
            
            # 使用 SQL + RAG
            tools = ToolFactory.create_tools(llm, ["sql", "rag"])
            ```
        """
        if tool_groups is None:
            return ToolFactory.create_all_tools(llm)
        
        tools = []
        for group in tool_groups:
            if group == "sql":
                tools.extend(ToolFactory.create_sql_tools(llm))
            elif group == "rag":
                tools.extend(ToolFactory.create_rag_tools())
            elif group == "all":
                return ToolFactory.create_all_tools(llm)
            else:
                logger.warning(f"未知的工具组: {group}")
        
        logger.info(f"创建工具组 {tool_groups}: {[t.name for t in tools]}")
        return tools
