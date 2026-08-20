"""
SQL 数据库工具模块

提供 LangChain SQLDatabaseToolkit 的初始化和获取接口
采用延迟初始化模式，避免模块导入时创建数据库连接
"""

from functools import lru_cache
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase
from langchain_core.language_models import BaseLanguageModel

from app.core.logger import logger
from app.core.database import sync_engine
from langchain_core.tools import BaseTool


@lru_cache()
def _get_db() -> SQLDatabase:
    """延迟获取 SQLDatabase 实例（单例模式）"""
    logger.debug("初始化 SQLDatabase 连接")
    return SQLDatabase(sync_engine)


def sql_toolkit(llm: BaseLanguageModel) -> list[BaseTool]:
    """获取 SQLDatabaseToolkit 实例
    
    Args:
        llm: LangChain LLM 实例
        
    Returns:
        list[BaseTool]: 配置好的 SQL 工具列表
        
    Note:
        首次调用时才会初始化数据库连接和工具包
    """
    try:
        db = _get_db()
        toolkit = SQLDatabaseToolkit(db=db, llm=llm)
        logger.info("SQLDatabaseToolkit 初始化成功")
        return toolkit.get_tools()
    except Exception as e:
        logger.error(f"SQL 工具初始化失败: {e}")
        raise
