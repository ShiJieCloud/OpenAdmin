from fastapi import APIRouter, Depends

from app.core.response import ResponseBuilder
from app.deps.service import (
    get_user_service,
    get_role_service,
    get_menu_service,
    get_dept_service,
    get_login_log_service,
    get_oper_log_service,
)
from app.schemas import DashboardOverviewResponse, LoginLogResponse, OperLogResponse
from app.schemas.base.response import ApiResponse
from app.services import (
    UserService,
    RoleService,
    MenuService,
    DeptService,
    LoginLogService,
    OperLogService
)


router = APIRouter()


@router.get(
    "/overview",
    response_model=ApiResponse[DashboardOverviewResponse],
    summary="获取系统概览",
    description="获取首页系统统计数据：用户总数、角色数量、菜单数量、部门数量"
)
async def get_system_overview(
    user_service: UserService = Depends(get_user_service),
    role_service: RoleService = Depends(get_role_service),
    menu_service: MenuService = Depends(get_menu_service),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    获取系统概览

    返回首页系统统计数据。
    接口需要用户登录方可访问。

    :return: 包含用户数、角色数、菜单数、部门数的统计数据
    """

    user_count = await user_service.count_users()
    role_count = await role_service.count_roles()
    menu_count = await menu_service.count_menus()
    dept_count = await dept_service.count_depts()
    
    overview = DashboardOverviewResponse(
        user_count=user_count,
        role_count=role_count,
        menu_count=menu_count,
        dept_count=dept_count,
    )
    
    return ResponseBuilder.success(overview)

@router.get(
    "/recent_login_logs",
    response_model=ApiResponse[list[LoginLogResponse]],
    summary="获取最近登录日志",
    description="获取最近登录日志，用于首页仪表盘展示"
)
async def get_recent_login_logs(
    limit: int = 10,
    login_log_service: LoginLogService = Depends(get_login_log_service)
):
    """
    获取最近登录日志

    返回最近的登录日志和操作日志，按时间倒序排列。
    接口需要用户登录方可访问。

    :param limit: 每种日志返回条数，默认10条
    :return: 包含最近登录日志和最近操作日志
    """
    logs = await login_log_service.get_recent_login_logs(limit)
    return ResponseBuilder.success(logs)

@router.get(
    "/recent_oper_logs",
    response_model=ApiResponse[list[OperLogResponse]],
    summary="获取最近系统操作日志",
    description="获取最近系统操作日志，用于首页仪表盘展示"
)
async def get_recent_oper_logs(
    limit: int = 10,
    oper_log_service: OperLogService = Depends(get_oper_log_service)
):
    """
    获取最近系统操作日志

    返回最近的系统操作日志，按时间倒序排列。
    接口需要用户登录方可访问。

    :param limit: 每种日志返回条数，默认10条
    :return: 包含最近系统操作日志
    """
    logs = await oper_log_service.get_recent_oper_logs(limit)
    return ResponseBuilder.success(logs)