from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime


class PermissionResponse(BaseModel):
    """权限响应"""

    id: int = Field(..., description="权限ID")
    menu_id: int = Field(..., description="所属菜单ID")
    name: str = Field(..., description="权限名称")
    code: str = Field(..., description="权限标识")
    type: int = Field(..., description="权限类型：0=按钮 1=接口")
    description: str | None = Field(None, description="权限描述")
    sort: int = Field(..., description="排序")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)
