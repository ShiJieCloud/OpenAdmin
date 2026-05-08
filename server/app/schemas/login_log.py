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


class LoginLogResponse(BaseModel):
    """登录日志响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="日志ID")
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="登录账号（手机号/邮箱/用户名）")
    operate_type: int = Field(..., description="操作类型：1-登录 2-登出")
    login_type: int = Field(..., description="登录类型：1-账号密码 2-短信 3-第三方 4-扫码 5-邮箱")
    login_status: int = Field(..., description="状态：0-成功 1-失败")
    fail_reason: str | None = Field(None, description="失败原因")
    login_ip: str = Field(..., description="IP地址")
    login_location: str | None = Field(None, description="登录地点")
    device_type: int | None = Field(None, description="设备：0-未知 1-PC 2-移动端 3-平板")
    os_name: str | None = Field(None, description="操作系统")
    browser_name: str | None = Field(None, description="浏览器")
    user_agent: str | None = Field(None, description="UA信息")
    operate_time: datetime = Field(..., description="操作时间（登录/登出时间）")
    remark: str | None = Field(None, description="备注")