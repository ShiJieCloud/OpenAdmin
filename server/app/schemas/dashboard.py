from pydantic import BaseModel, Field, ConfigDict

class DashboardOverviewResponse(BaseModel):
    """仪表盘首页统计概览返回模型"""

    model_config = ConfigDict(from_attributes=True)

    user_count: int = Field(0, description="系统用户总数量")
    role_count: int = Field(0, description="角色总数量")
    menu_count: int = Field(0, description="菜单总数量")
    dept_count: int = Field(0, description="部门总数量")
