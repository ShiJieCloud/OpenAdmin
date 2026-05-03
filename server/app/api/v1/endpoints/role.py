from fastapi import APIRouter, Depends, Path, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_role_service
from app.schemas.base.response import ApiResponse, PaginationResponse
from app.schemas.role import RoleInfoResponse, RoleListQueryRequest
from app.services import RoleService

router = APIRouter()


@router.get(
    "/{role_id}",
    response_model=ApiResponse[RoleInfoResponse],
    # dependencies=[Depends(has_perm(PermCode.Role.READ))],
    summary="获取角色详情",
    description="根据角色唯一ID查询指定角色的详细信息（需要具备角色查看权限）"
)
async def get_role_info(
    role_id: int = Path(..., description="角色ID", ge=1, examples=[1]),
    role_service: RoleService = Depends(get_role_service)
):
    """
    获取角色详情

    根据角色ID查询角色完整信息，包括角色名称、编码、描述、状态等，
    接口需要用户登录并拥有角色查看权限方可访问。

    :param role_id: 目标角色的唯一标识ID
    :return: 返回角色详细信息
    :raises BusinessError: 角色不存在
    """
    role = await role_service.get_role(role_id)
    role_info = RoleInfoResponse.model_validate(role)
    return ResponseBuilder.success(role_info)


@router.post(
    "/list",
    response_model=PaginationResponse[RoleInfoResponse],
    # dependencies=[Depends(has_perm(PermCode.Role.READ))],
    summary="分页查询角色列表",
    description="分页获取角色列表，支持多条件筛选（需要具备角色查看权限）"
)
async def get_role_list(
    query: RoleListQueryRequest = Body(..., description="查询条件"),
    role_service: RoleService = Depends(get_role_service)
):
    """
    分页查询角色列表

    支持的条件筛选：
    - 角色名称（模糊查询）
    - 角色编码（模糊查询）
    - 状态（精确匹配）

    结果按显示顺序升序、创建时间倒序排列。
    接口需要用户登录并拥有角色查看权限方可访问。

    :param query: 分页参数和筛选条件
    :return: 返回分页角色列表
    """
    roles, total, pages, page_num = await role_service.get_role_list(query)
    records = [RoleInfoResponse.model_validate(role) for role in roles]
    return ResponseBuilder.pagination(records, total, page_num, query.page_size)
