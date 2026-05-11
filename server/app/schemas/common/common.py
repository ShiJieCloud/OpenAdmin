from pydantic import BaseModel, Field


class UserAgentInfo(BaseModel):
    """User-Agent 解析结果模型"""
    
    device_type: str = Field(default=0, description="设备类型")
    os: str = Field(default="", description="操作系统名称")
    browser: str = Field(default="", description="浏览器名称")
    user_agent: str = Field(default="", description="原始UA字符串")
