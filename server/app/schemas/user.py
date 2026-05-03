from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserCreateRequest(BaseModel):
    """创建用户请求"""

    username: str = Field(..., description="登录账号", min_length=3, max_length=50, example="admin")
    password: str = Field(..., description="登录密码", min_length=6, max_length=50, example="123456")
    nickname: str | None = Field(None, description="用户昵称/姓名", max_length=50, example="管理员")
    avatar: str | None = Field(None, description="头像URL", max_length=255)
    email: str | None = Field(None, description="邮箱", max_length=100, example="admin@example.com")
    phone: str | None = Field(None, description="手机号", max_length=20, example="13800138000")
    sex: int = Field(0, description="性别：0=未知 1=男 2=女", ge=0, le=2, example=0)
    dept_id: int | None = Field(None, description="所属部门ID", ge=1)
    remark: str | None = Field(None, description="备注", max_length=500)


class UserResetPasswordRequest(BaseModel):
    """重置用户密码请求"""

    user_id: int = Field(..., description="用户ID", ge=1, example=1001)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=50, example="123456")


class UserUpdateStatusRequest(BaseModel):
    """修改用户状态请求"""

    user_id: int = Field(..., description="用户ID", ge=1, example=1001)
    status: int = Field(..., description="目标状态：0=正常 1=禁用 4=冻结", ge=0, le=4, example=1)


class UserUpdateRequest(BaseModel):
    """编辑用户基础信息请求"""

    user_id: int = Field(..., description="用户ID", ge=1, example=1001)
    nickname: str | None = Field(None, description="用户昵称/姓名", max_length=50, example="管理员")
    avatar: str | None = Field(None, description="头像URL", max_length=255)
    email: str | None = Field(None, description="邮箱", max_length=100, example="admin@example.com")
    phone: str | None = Field(None, description="手机号", max_length=20, example="13800138000")
    sex: int | None = Field(None, description="性别：0=未知 1=男 2=女", ge=0, le=2, example=0)
    dept_id: int | None = Field(None, description="所属部门ID", ge=1)
    remark: str | None = Field(None, description="备注", max_length=500)


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
