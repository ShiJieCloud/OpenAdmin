from app.config.base import BaseConfig
from pydantic import Field


class SearchConfig(BaseConfig):
    """搜索服务配置"""
    TAVILY_API_KEY: str = Field(default="", description="Tavily API 密钥")


search_config = SearchConfig()
