from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer, SerializationInfo, computed_field

HOUR_SECONDS = 3600
MINUTE_SECONDS = 60

class UserRoleAssignRequest(BaseModel):
    """用户角色分配请求（对比差异合并）

    前端传入用户调整后的所有角色ID
    后端对比差异：
    - 数据库没有，前端有 → 新增
    - 数据库有，前端没有 → 删除
    - 两边都有 → 保持不变
    """

    user_id: int = Field(..., description="用户ID", ge=1, example=1001)
    role_ids: list[int] = Field(..., description="调整后的所有角色ID列表", example=[1, 2, 3])


class UserCreateRequest(BaseModel):
    """创建用户请求"""

    username: str = Field(..., description="登录账号", min_length=3, max_length=50, example="admin")
    password: str = Field(..., description="登录密码", min_length=6, max_length=50, example="123456")
    nickname: str | None = Field(None, description="用户昵称/姓名", max_length=50, example="管理员")
    avatar: str | None = Field(None, description="头像URL", max_length=255)
    email: str = Field(..., description="邮箱", max_length=100, example="admin@example.com")
    phone: str | None = Field(None, description="手机号", max_length=20, example="13800138000")
    sex: int = Field(0, description="性别：0=未知 1=男 2=女", ge=0, le=2, example=0)
    dept_id: int | None = Field(None, description="所属部门ID", ge=1)
    post_ids: list[int] = Field(default_factory=list, description="岗位ID列表（一人多岗）", example=[1, 2, 3])
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
    post_ids: list[int] | None = Field(None, description="岗位ID列表（一人多岗）", example=[1, 2, 3])
    remark: str | None = Field(None, description="备注", max_length=500)


class UserListQueryRequest(BaseModel):
    """用户列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    username: str | None = Field(None, description="登录账号（模糊查询）", max_length=50)
    nickname: str | None = Field(None, description="用户昵称（模糊查询）", max_length=50)
    email: str | None = Field(None, description="邮箱（模糊查询）", max_length=100)
    phone: str | None = Field(None, description="手机号（模糊查询）", max_length=20)
    status: int | None = Field(None, description="账号状态：0=正常 1=禁用 2=锁定 4=冻结", ge=0, le=4)
    dept_id: int | None = Field(None, description="所属部门ID", ge=1)


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
    dept_name: str | None = Field(None, description="所属部门名称")
    post_ids: list[int] = Field(default_factory=list, description="岗位ID列表（一人多岗）")
    last_login_ip: str | None = Field(None, description="最后登录IP")
    last_login_date: datetime | None = Field(None, description="最后登录时间")
    create_time: datetime = Field(..., description="创建时间")

    @field_serializer("create_time")
    def format_datetime(dt: datetime | None, _info: SerializationInfo):
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")

class OnlineUserQueryRequest(BaseModel):
    """在线用户列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)

class OnlineUserInfoResponse(BaseModel):
    """在线用户列表响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="登录账号")
    nickname: str | None = Field(None, description="用户昵称/姓名")
    avatar: str | None = Field(None, description="头像URL")
    login_ip: str | None = Field(None, description="登录IP地址")
    login_address: str | None = Field(None, description="登录地址")
    login_time: datetime | None = Field(None, description="登录时间")
    login_device: str | None = Field(None, description="登录设备")

    @field_serializer("login_time")
    def format_datetime(dt: datetime | None, _info: SerializationInfo):
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    @computed_field(return_type=str | None)
    @property
    def online_duration(self) -> str | None:
        """
        根据登录时间自动格式化在线时长，由Schema自行派生，业务层无需处理
        格式示例：3天 2小时 / 5小时 23分钟 / 12分钟
        """
        login_time: datetime | None = self.login_time
        if not login_time:
            return None

        # 优先使用带时区的 now，根据你的项目调整
        now = datetime.now()
        # now = datetime.now(tz=UTC)
        delta: timedelta = now - login_time

        days = delta.days
        remain_sec = delta.seconds

        hours = remain_sec // HOUR_SECONDS
        minutes = (remain_sec % HOUR_SECONDS) // MINUTE_SECONDS

        if days > 0:
            return f"{days} 天 {hours} 小时"
        if hours > 0:
            return f"{hours} 小时 {minutes} 分钟"
        return f"{minutes} 分钟"
