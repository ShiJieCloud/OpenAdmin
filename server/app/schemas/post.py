from datetime import datetime
from pydantic import BaseModel, Field


class PostListQueryRequest(BaseModel):
    """岗位列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=10)
    post_name: str | None = Field(None, description="岗位名称（模糊查询）", max_length=50)
    status: int | None = Field(None, description="状态：0=启用 1=禁用", ge=0, le=1)
    dept_ids: list[int] | None = Field(None, description="所属部门ID列表")


class PostCreateRequest(BaseModel):
    """创建岗位请求"""

    post_name: str = Field(..., description="岗位名称", min_length=2, max_length=50)
    dept_id: int | None = Field(None, description="所属部门ID", ge=0)
    sort: int = Field(999, description="显示顺序", ge=0)
    status: int = Field(0, description="状态：0=启用 1=禁用", ge=0, le=1)
    remark: str = Field("", description="备注", max_length=200)


class PostUpdateRequest(BaseModel):
    """编辑岗位请求"""

    post_id: int = Field(..., description="岗位ID", ge=1)
    post_name: str | None = Field(None, description="岗位名称", min_length=2, max_length=50)
    dept_id: int | None = Field(None, description="所属部门ID", ge=0)
    sort: int | None = Field(None, description="显示顺序", ge=0)
    status: int | None = Field(None, description="状态：0=启用 1=禁用", ge=0, le=1)
    remark: str | None = Field(None, description="备注", max_length=200)


class PostBatchDeleteRequest(BaseModel):
    """批量删除岗位请求"""

    post_ids: list[int] = Field(..., description="岗位ID列表", min_length=1)


class PostInfoResponse(BaseModel):
    """岗位信息响应"""

    model_config = {"from_attributes": True}

    id: int = Field(..., description="岗位ID")
    post_name: str = Field(..., description="岗位名称")
    dept_id: int | None = Field(None, description="所属部门ID")
    dept_name: str | None = Field(None, description="所属部门名称")
    sort: int = Field(..., description="显示顺序")
    status: int = Field(..., description="状态：0=启用 1=禁用")
    remark: str = Field("", description="备注")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")


class PostRoleAssignRequest(BaseModel):
    """岗位角色分配请求（对比差异合并）

    前端传入岗位调整后的所有角色ID
    后端对比差异：
    - 数据库没有，前端有 → 新增
    - 数据库有，前端没有 → 删除
    - 两边都有 → 保持不变
    """

    role_ids: list[int] = Field(..., description="调整后的所有角色ID列表", example=[1, 2, 3])
