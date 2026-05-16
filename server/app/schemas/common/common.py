from pydantic import BaseModel, Field


class UserAgentInfo(BaseModel):
    """User-Agent 解析结果模型"""
    
    device_type: str | None = Field(default=None, description="设备类型")
    os: str | None = Field(default=None, description="操作系统名称")
    browser: str | None = Field(default=None, description="浏览器名称")
    user_agent: str | None = Field(default=None, description="原始UA字符串")
