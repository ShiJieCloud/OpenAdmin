from pydantic import BaseModel, Field
from typing import Optional, List
from pydantic import ConfigDict
from datetime import datetime


class MenuCreateRequest(BaseModel):
    """菜单创建请求"""

    menu_name: str = Field(..., description="菜单名称", max_length=64)
    parent_id: int = Field(0, description="父菜单ID，顶级菜单为0")
    sort: int = Field(0, description="排序号，越小越靠前")
    path: str = Field("", description="前端路由地址", max_length=255)
    component: Optional[str] = Field(None, description="前端组件路径", max_length=255)
    menu_type: int = Field(..., description="菜单类型：0=目录 1=页面")
    icon: str = Field("", description="菜单图标", max_length=128)
    is_hidden: int = Field(0, description="是否隐藏：0=显示 1=隐藏")
    is_frame: int = Field(0, description="是否内嵌：0=否 1=是")
    status: int = Field(0, description="状态：0=启用 1=禁用")


class MenuUpdateRequest(BaseModel):
    """菜单更新请求"""

    menu_name: Optional[str] = Field(None, description="菜单名称", max_length=64)
    parent_id: Optional[int] = Field(None, description="父菜单ID，顶级菜单为0")
    sort: Optional[int] = Field(None, description="排序号，越小越靠前")
    path: Optional[str] = Field(None, description="前端路由地址", max_length=255)
    component: Optional[str] = Field(None, description="前端组件路径", max_length=255)
    menu_type: Optional[int] = Field(None, description="菜单类型：0=目录 1=页面")
    icon: Optional[str] = Field(None, description="菜单图标", max_length=128)
    is_hidden: Optional[int] = Field(None, description="是否隐藏：0=显示 1=隐藏")
    is_frame: Optional[int] = Field(None, description="是否内嵌：0=否 1=是")
    status: Optional[int] = Field(None, description="状态：0=启用 1=禁用")


class MenuUpdateStatusRequest(BaseModel):
    """菜单更新状态请求"""

    menu_id: int = Field(..., description="菜单ID")
    status: int = Field(..., description="状态：0=启用 1=禁用")


class MenuDeleteRequest(BaseModel):
    """菜单删除请求"""

    menu_ids: list[int] = Field(..., description="菜单ID列表")


class MenuResponse(BaseModel):
    """菜单响应"""

    id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    parent_id: int = Field(..., description="父菜单ID")
    sort: int = Field(..., description="排序号，越小越靠前")
    path: str = Field(..., description="前端路由地址")
    component: Optional[str] = Field(None, description="前端组件路径")  
    menu_type: int = Field(..., description="菜单类型：0=目录 1=页面")
    icon: str = Field(..., description="菜单图标")
    is_hidden: int = Field(..., description="是否隐藏：0=显示 1=隐藏")
    is_frame: int = Field(..., description="是否内嵌：0=否 1=是")
    status: int = Field(..., description="状态：0=启用 1=禁用")
    create_time: datetime = Field(..., description="创建时间")
    update_time: datetime = Field(..., description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class MenuTreeResponse(BaseModel):
    """菜单树响应（递归结构）"""

    id: int = Field(..., description="菜单ID")
    menu_name: str = Field(..., description="菜单名称")
    parent_id: int = Field(..., description="父菜单ID")
    sort: int = Field(..., description="排序号，越小越靠前")
    path: str = Field(..., description="前端路由地址")
    component: Optional[str] = Field(None, description="前端组件路径")
    menu_type: int = Field(..., description="菜单类型：0=目录 1=页面")
    icon: str = Field(..., description="菜单图标")
    is_hidden: int = Field(..., description="是否隐藏：0=显示 1=隐藏")
    is_frame: int = Field(..., description="是否内嵌：0=否 1=是")
    children: List["MenuTreeResponse"] = Field([], description="子菜单列表")

    model_config = ConfigDict(from_attributes=True)


MenuTreeResponse.model_rebuild()
