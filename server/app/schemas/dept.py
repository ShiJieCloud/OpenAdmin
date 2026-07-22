from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DeptCreateRequest(BaseModel):
    """创建部门请求"""

    parent_id: int = Field(0, description="父级部门ID（0=顶级）", ge=0, example=0)
    dept_name: str = Field(..., description="部门名称", min_length=2, max_length=50, example="技术部")
    sort: int = Field(999, description="显示顺序（越小越靠前）", ge=0, example=1)
    status: int = Field(0, description="状态：0=启用 1=禁用", ge=0, le=1, example=0)


class DeptUpdateRequest(BaseModel):
    """编辑部门请求"""

    dept_id: int = Field(..., description="部门ID", ge=1, example=1)
    parent_id: int | None = Field(None, description="父级部门ID", ge=0)
    dept_name: str | None = Field(None, description="部门名称", min_length=2, max_length=50)
    sort: int | None = Field(None, description="显示顺序", ge=0)
    status: int | None = Field(None, description="状态：0=启用 1=禁用", ge=0, le=1)


class DeptInfoResponse(BaseModel):
    """部门信息响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="部门ID")
    parent_id: int = Field(..., description="父级部门ID")
    dept_name: str = Field(..., description="部门名称")
    sort: int = Field(..., description="显示顺序")
    status: int = Field(..., description="状态：0=启用 1=禁用")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")
