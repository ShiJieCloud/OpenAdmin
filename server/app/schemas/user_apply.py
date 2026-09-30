from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer, SerializationInfo


class UserApplyListQueryRequest(BaseModel):
    """用户注册申请列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    username: str | None = Field(None, description="登录账号（模糊查询）", max_length=50)
    phone: str | None = Field(None, description="手机号（模糊查询）", max_length=20)
    status: int | None = Field(None, description="审核状态：0=待审核 1=已通过 2=已拒绝 3=撤销", ge=0, le=3)


class UserApplyRejectRequest(BaseModel):
    """拒绝用户注册申请请求"""

    reason: str = Field(..., description="拒绝原因", min_length=1, max_length=500, example="信息填写不规范")


class UserApplyPassRequest(BaseModel):
    """审批通过请求"""

    dept_id: int = Field(..., description="所属部门ID", ge=1, example=1001)
    post_ids: list[int] = Field(..., description="岗位ID列表（一人多岗，必须属于上送部门，不可为空）", min_length=1, example=[1, 2])


class UserApplyInfoResponse(BaseModel):
    """用户注册申请信息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="申请ID")
    username: str = Field(..., description="登录账号")
    phone: str | None = Field(None, description="手机号")
    status: int = Field(..., description="审核状态：0=待审核 1=已通过 2=已拒绝 3=撤销")
    audit_user_id: int | None = Field(None, description="审批管理员ID")
    audit_time: datetime | None = Field(None, description="审批时间")
    audit_reason: str | None = Field(None, description="审批意见/拒绝原因")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    @field_serializer("audit_time", "create_time", "update_time")
    def format_datetime(dt: datetime | None, _info: SerializationInfo):
        if dt is None:
            return None
        return dt.strftime("%Y-%m-%d %H:%M:%S")
