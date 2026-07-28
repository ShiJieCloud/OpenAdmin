from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class PermissionResponse(BaseModel):
    """权限响应"""

    id: int = Field(..., description="权限ID")
    menu_id: int = Field(..., description="所属菜单ID")
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限标识")
    description: str | None = Field(None, description="权限描述")
    sort: int = Field(..., description="排序")
    status: int = Field(..., description="状态：0=正常 1=停用")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class PermissionCreateRequest(BaseModel):
    """创建权限请求"""

    menu_id: int = Field(..., description="所属菜单ID", ge=0, example=1)
    name: str = Field(..., description="权限名称", min_length=2, max_length=64, example="查看用户")
    code: str = Field(..., description="权限标识", min_length=2, max_length=128, example="system:user:read")
    sort: int = Field(0, description="排序", ge=0, example=1)
    status: int = Field(0, description="状态：0=正常 1=停用", ge=0, le=1, example=0)
    description: str | None = Field(None, description="权限描述", max_length=255)


class PermissionUpdateRequest(BaseModel):
    """编辑权限请求"""

    perm_id: int = Field(..., description="权限ID", ge=1, example=1)
    menu_id: int | None = Field(None, description="所属菜单ID", ge=0)
    name: str | None = Field(None, description="权限名称", min_length=2, max_length=64)
    code: str | None = Field(None, description="权限标识", min_length=2, max_length=128)
    sort: int | None = Field(None, description="排序", ge=0)
    status: int | None = Field(None, description="状态：0=正常 1=停用", ge=0, le=1)
    description: str | None = Field(None, description="权限描述", max_length=255)


class PermissionListQueryRequest(BaseModel):
    """权限列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    name: str | None = Field(None, description="权限名称（模糊查询）", max_length=64)
    code: str | None = Field(None, description="权限标识（模糊查询）", max_length=128)
    status: int | None = Field(None, description="状态：0=正常 1=停用", ge=0, le=1)
    menu_id: int | None = Field(None, description="所属菜单ID", ge=0)
