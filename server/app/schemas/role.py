from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RoleCreateRequest(BaseModel):
    """创建角色请求"""

    role_name: str = Field(..., description="角色名称", min_length=2, max_length=50, example="管理员")
    role_code: str = Field(..., description="角色唯一编码", min_length=2, max_length=50, example="ADMIN")
    sort: int = Field(0, description="显示顺序", ge=0, example=1)
    description: str | None = Field(None, description="角色描述", max_length=255)
    status: int = Field(0, description="状态：0=启用 1=禁用", ge=0, le=1, example=0)


class RoleUpdateRequest(BaseModel):
    """编辑角色请求"""

    role_id: int = Field(..., description="角色ID", ge=1, example=1)
    role_name: str | None = Field(None, description="角色名称", min_length=2, max_length=50)
    role_code: str | None = Field(None, description="角色唯一编码", min_length=2, max_length=50)
    sort: int | None = Field(None, description="显示顺序", ge=0)
    description: str | None = Field(None, description="角色描述", max_length=255)
    status: int | None = Field(None, description="状态：0=启用 1=禁用", ge=0, le=1)


class RoleUpdateStatusRequest(BaseModel):
    """更新角色状态请求"""

    role_id: int = Field(..., description="角色ID", ge=1, example=1)
    status: int = Field(..., description="状态：0=启用 1=禁用", ge=0, le=1, example=0)


class RoleListQueryRequest(BaseModel):
    """角色列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    role_name: str | None = Field(None, description="角色名称（模糊查询）", max_length=50)
    role_code: str | None = Field(None, description="角色编码（模糊查询）", max_length=50)
    status: int | None = Field(None, description="状态：0=启用 1=禁用", ge=0, le=1)


class RoleInfoResponse(BaseModel):
    """角色信息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="角色ID")
    role_name: str = Field(..., description="角色名称")
    role_code: str = Field(..., description="角色唯一编码")
    sort: int = Field(..., description="显示顺序")
    description: str | None = Field(None, description="角色描述")
    status: int = Field(..., description="状态：0=启用 1=禁用")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
