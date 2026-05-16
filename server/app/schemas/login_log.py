from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LoginLogListQueryRequest(BaseModel):
    """登录日志列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    user_id: int | None = Field(None, description="用户ID", ge=1)
    username: str | None = Field(None, description="登录账号（模糊查询）", max_length=64)
    operate_type: int | None = Field(None, description="操作类型：1-登录 2-登出", ge=1, le=2)
    login_type: int | None = Field(None, description="登录类型：1-账号密码 2-短信 3-第三方 4-扫码 5-邮箱", ge=1, le=5)
    login_status: int | None = Field(None, description="登录状态：0-成功 1-失败", ge=0, le=1)
    login_ip: str | None = Field(None, description="登录IP（模糊查询）", max_length=45)
    start_time: datetime | None = Field(None, description="开始时间")
    end_time: datetime | None = Field(None, description="结束时间")


class LoginLogCreateRequest(BaseModel):
    """登录日志创建请求"""
    model_config = ConfigDict(from_attributes=True)

    user_id: int | None = Field(None, description="用户ID")
    username: str = Field(..., description="登录账号")
    login_type: int | None = Field(None, description="登录类型 1-账号密码 2-短信 3-第三方 4-扫码 5-单点（登出时为NULL）")
    operate_type: int = Field(..., description="操作类型 1-登录 2-登出")
    operate_status: int = Field(..., description="状态 0-失败 1-成功")
    fail_reason: str | None = Field(None, description="失败原因")
    client_ip: str = Field(..., description="客户端IP")
    ip_country: str | None = Field(None, description="国家")
    ip_province: str | None = Field(None, description="省份/直辖市")
    ip_city: str | None = Field(None, description="城市")
    ip_location: str | None = Field(None, description="完整属地：国家-省-市")
    device_type: str | None = Field(None, description="设备类型")
    browser: str | None = Field(None, description="浏览器")
    trace_id: str = Field(..., description="链路追踪ID")


class LoginLogResponse(BaseModel):
    """登录日志响应"""
    pass