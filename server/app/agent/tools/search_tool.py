"""
网络搜索工具模块

基于 Tavily 搜索 API，为 Agent 提供网络搜索能力
采用延迟初始化模式，避免模块导入时创建搜索客户端
"""

from functools import lru_cache
from langchain_core.tools import BaseTool

from app.core.logger import logger


@lru_cache()
def get_search_tool() -> BaseTool:
    """延迟获取搜索工具（单例模式）
    
    Returns:
        BaseTool: 配置好的搜索工具
        
    Note:
        首次调用时才会初始化 Tavily 客户端
    """
    try:
        from langchain_tavily import TavilySearch
        from app.config.search import search_config
        
        tool = TavilySearch(
            max_results=5,
            topic="general",
            tavily_api_key=search_config.TAVILY_API_KEY,
            include_raw_content=False,
        )
        
        logger.info("搜索工具初始化成功")
        return tool
    except Exception as e:
        logger.error(f"搜索工具初始化失败: {e}")
        raise