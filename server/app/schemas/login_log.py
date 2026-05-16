from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LoginLogListQueryRequest(BaseModel):
    """登录日志列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    user_id: int | None = Field(None, description="用户ID", ge=1)
    username: str | None = Field(None, description="登录账号（模糊查询）", max_length=64)
    client_ip: str | None = Field(None, description="登录IP（模糊查询）", max_length=50)
    start_time: datetime | None = Field(None, description="开始时间")
    end_time: datetime | None = Field(None, description="结束时间")


class LoginLogCreateRequest(BaseModel):
    """登录日志创建请求"""
    model_config = ConfigDict(from_attributes=True)

    trace_id: str = Field(..., description="链路追踪ID", max_length=64)
    user_id: int | None = Field(None, description="用户ID")
    username: str = Field(..., description="用户名称", max_length=50)
    response_code: str | None = Field(None, description="响应码", max_length=32)
    response_msg: str | None = Field(None, description="响应信息/错误描述", max_length=512)
    client_ip: str = Field(..., description="客户端IP", max_length=50)
    ip_country: str | None = Field(None, description="国家", max_length=32)
    ip_province: str | None = Field(None, description="省份/直辖市", max_length=32)
    ip_city: str | None = Field(None, description="城市", max_length=32)
    os: str | None = Field(None, description="操作系统", max_length=30)
    browser: str | None = Field(None, description="浏览器", max_length=100)
    user_agent: str | None = Field(None, description="客户端标识", max_length=512)


class LoginLogResponse(BaseModel):
    """登录日志响应"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="日志ID")
    trace_id: str = Field(..., description="链路追踪ID")
    user_id: int | None = Field(None, description="用户ID")
    username: str = Field(..., description="用户名称")
    response_code: str | None = Field(None, description="响应码")
    response_msg: str | None = Field(None, description="响应信息/错误描述")
    client_ip: str = Field(..., description="客户端IP")
    ip_country: str | None = Field(None, description="国家")
    ip_province: str | None = Field(None, description="省份/直辖市")
    ip_city: str | None = Field(None, description="城市")
    os: str | None = Field(None, description="操作系统")
    browser: str | None = Field(None, description="浏览器")
    user_agent: str | None = Field(None, description="客户端标识")
    create_time: datetime = Field(..., description="创建时间")
