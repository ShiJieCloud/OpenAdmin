from fastapi import APIRouter, Depends, Path, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder, ApiResponse
from app.deps.permission import has_perm
from app.deps.service import get_permission_service
from app.schemas.base.response import PaginationResponse
from app.schemas.permission import (
    PermissionResponse,
    PermissionCreateRequest,
    PermissionUpdateRequest,
    PermissionListQueryRequest,
)
from app.services import PermissionService

router = APIRouter()


@router.get(
    "",
    response_model=ApiResponse[list[PermissionResponse]],
    dependencies=[Depends(has_perm(PermCode.Perm.READ))],
    summary="获取所有权限列表",
    description="获取系统中所有权限列表（需要具备权限查看权限）"
)
async def get_all_permissions(
    permission_service: PermissionService = Depends(get_permission_service)
):
    """
    获取所有权限列表

    权限：`system:perm:read`
    """
    permissions = await permission_service.get_all_permissions()
    perm_list = [PermissionResponse.model_validate(perm) for perm in permissions]
    return ResponseBuilder.success(data=perm_list)


@router.post(
    "/list",
    response_model=PaginationResponse[PermissionResponse],
    dependencies=[Depends(has_perm(PermCode.Perm.READ))],
    summary="分页查询权限列表",
    description="分页获取权限列表，支持多条件筛选（需要具备权限查看权限）"
)
async def get_permission_list(
    query: PermissionListQueryRequest = Body(..., description="查询条件"),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """
    分页查询权限列表

    支持的条件筛选：
    - 权限名称（模糊查询）
    - 权限编码（模糊查询）
    - 权限类型（精确匹配）
    - 菜单ID（精确匹配）

    结果按排序字段升序、创建时间倒序排列。
    接口需要用户登录并拥有权限查看权限方可访问。

    :param query: 分页参数和筛选条件
    :return: 返回分页权限列表
    """
    perms, total, pages, page_num = await permission_service.get_permission_list(query)
    records = [PermissionResponse.model_validate(perm) for perm in perms]
    return ResponseBuilder.pagination(records, total, page_num, query.page_size)


@router.post(
    "",
    response_model=ApiResponse[PermissionResponse],
    dependencies=[Depends(has_perm(PermCode.Perm.CREATE))],
    summary="创建权限",
    description="创建新权限（需要具备权限创建权限）"
)
async def create_permission(
    req: PermissionCreateRequest = Body(..., description="创建权限请求"),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """
    创建权限

    权限编码必须全局唯一。
    接口需要用户登录并拥有权限创建权限方可访问。

    :param req: 创建权限信息
    :return: 返回创建后的权限详情
    :raises BusinessError: 权限编码已存在
    """
    perm = await permission_service.create_permission(req)
    perm_info = PermissionResponse.model_validate(perm)
    return ResponseBuilder.success(perm_info)


@router.put(
    "",
    response_model=ApiResponse[PermissionResponse],
    dependencies=[Depends(has_perm(PermCode.Perm.UPDATE))],
    summary="编辑权限",
    description="更新权限信息（需要具备权限编辑权限）"
)
async def update_permission(
    req: PermissionUpdateRequest = Body(..., description="编辑权限请求"),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """
    编辑权限

    权限编码必须全局唯一（排除自身）。
    接口需要用户登录并拥有权限编辑权限方可访问。

    :param req: 编辑权限信息
    :return: 返回更新后的权限详情
    :raises BusinessError: 权限不存在 / 权限编码已存在
    """
    perm = await permission_service.update_permission(req)
    perm_info = PermissionResponse.model_validate(perm)
    return ResponseBuilder.success(perm_info)


@router.delete(
    "/{perm_id}",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Perm.DELETE))],
    summary="删除权限",
    description="删除权限（需要具备权限删除权限）"
)
async def delete_permission(
    perm_id: int = Path(..., description="权限ID", ge=1, examples=[1]),
    permission_service: PermissionService = Depends(get_permission_service)
):
    """
    删除权限

    物理删除权限，同时删除角色权限关联表中的数据。
    接口需要用户登录并拥有权限删除权限方可访问。

    :param perm_id: 要删除的权限ID
    :return: 无返回数据
    :raises BusinessError: 权限不存在
    """
    await permission_service.delete_permission(perm_id)
    return ResponseBuilder.success(message="删除成功")
