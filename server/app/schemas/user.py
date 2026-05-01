from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserInfoResponse(BaseModel):
    """用户信息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="登录账号")
    nickname: str | None = Field(None, description="用户昵称/姓名")
    avatar: str | None = Field(None, description="头像URL")
    email: str | None = Field(None, description="邮箱")
    phone: str | None = Field(None, description="手机号")
    sex: int = Field(..., description="性别：0=未知 1=男 2=女")
    status: int = Field(..., description="账号状态：0=正常 1=禁用 2=锁定 3=注销 4=冻结")
    dept_id: int | None = Field(None, description="所属部门ID")
    post_id: int | None = Field(None, description="所属岗位ID")
    last_login_ip: str | None = Field(None, description="最后登录IP")
    last_login_date: datetime | None = Field(None, description="最后登录时间")
    create_time: datetime = Field(..., description="创建时间")
