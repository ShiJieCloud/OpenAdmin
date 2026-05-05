from fastapi import APIRouter, Depends, Path, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_role_service
from app.schemas.base.response import ApiResponse, PaginationResponse
from app.schemas.role import RoleInfoResponse, RoleCreateRequest, RoleUpdateRequest, RoleUpdateStatusRequest, RoleListQueryRequest
from app.services import RoleService

router = APIRouter()


@router.get(
    "/{role_id}",
    response_model=ApiResponse[RoleInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Role.READ))],
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
    dependencies=[Depends(has_perm(PermCode.Role.LIST))],
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


@router.post(
    "",
    response_model=ApiResponse[RoleInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Role.CREATE))],
    summary="创建角色",
    description="创建新角色（需要具备角色创建权限）"
)
async def create_role(
    req: RoleCreateRequest = Body(..., description="创建角色请求"),
    role_service: RoleService = Depends(get_role_service)
):
    """
    创建角色

    角色编码必须全局唯一。
    接口需要用户登录并拥有角色创建权限方可访问。

    :param req: 创建角色信息
    :return: 返回创建后的角色详情
    :raises BusinessError: 角色编码已存在
    """
    role = await role_service.create_role(req)
    role_info = RoleInfoResponse.model_validate(role)
    return ResponseBuilder.success(role_info)


@router.put(
    "",
    response_model=ApiResponse[RoleInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Role.UPDATE))],
    summary="编辑角色",
    description="更新角色信息（需要具备角色编辑权限）"
)
async def update_role(
    req: RoleUpdateRequest = Body(..., description="编辑角色请求"),
    role_service: RoleService = Depends(get_role_service)
):
    """
    编辑角色

    角色编码必须全局唯一（排除自身）。
    接口需要用户登录并拥有角色编辑权限方可访问。

    :param req: 编辑角色信息
    :return: 返回更新后的角色详情
    :raises BusinessError: 角色不存在 / 角色编码已存在
    """
    role = await role_service.update_role(req)
    role_info = RoleInfoResponse.model_validate(role)
    return ResponseBuilder.success(role_info)


@router.delete(
    "/{role_id}",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Role.DELETE))],
    summary="删除角色",
    description="删除角色（需要具备角色删除权限）"
)
async def delete_role(
    role_id: int = Path(..., description="角色ID", ge=1, examples=[1]),
    role_service: RoleService = Depends(get_role_service)
):
    """
    删除角色

    物理删除角色。
    接口需要用户登录并拥有角色删除权限方可访问。

    :param role_id: 要删除的角色ID
    :return: 无返回数据
    :raises BusinessError: 角色不存在
    """
    await role_service.delete_role(role_id)
    return ResponseBuilder.success(message="删除成功")


@router.put(
    "/status",
    response_model=ApiResponse[RoleInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Role.UPDATE))],
    summary="更新角色状态",
    description="启用或禁用角色（需要具备角色编辑权限）"
)
async def update_role_status(
    req: RoleUpdateStatusRequest = Body(..., description="更新角色状态请求"),
    role_service: RoleService = Depends(get_role_service)
):
    """
    更新角色状态

    启用或禁用角色。
    接口需要用户登录并拥有角色编辑权限方可访问。

    :param req: 更新角色状态请求
    :return: 更新后的角色信息
    :raises BusinessError: 角色不存在
    """
    role = await role_service.update_role_status(req)
    role_info = RoleInfoResponse.model_validate(role)
    return ResponseBuilder.success(role_info)
