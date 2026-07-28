from fastapi import APIRouter, Body, Depends, Path

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_post_service, get_dept_service
from app.schemas.base.response import ApiResponse, PaginationResponse
from app.schemas.post import (
    PostBatchDeleteRequest,
    PostCreateRequest,
    PostInfoResponse,
    PostListQueryRequest,
    PostUpdateRequest,
    PostRoleAssignRequest
)
from app.services import DeptService, PostService

router = APIRouter()


@router.post(
    "/list",
    response_model=PaginationResponse[PostInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Post.READ))],
    summary="分页查询岗位列表",
    description="分页获取岗位列表，支持按岗位名称、状态、部门ID列表筛选"
)
async def get_post_list(
    query: PostListQueryRequest = Body(..., description="查询条件"),
    post_service: PostService = Depends(get_post_service),
    dept_service: DeptService = Depends(get_dept_service),
):
    """
    分页查询岗位列表

    支持按岗位名称、状态、部门ID列表筛选。
    接口需要用户登录并拥有岗位读取权限方可访问。

    :param query: 查询条件（包含分页参数和筛选条件）
    :return: 返回分页岗位列表
    """
    post_list, total = await post_service.list_posts(query)

    # 填充部门名称
    # 1. 提取所有部门ID，去重
    dept_ids = {post.dept_id for post in post_list if post.dept_id}
    if dept_ids:
        # 一次性批量查询所有部门（只查需要的字段，不要查全量）
        dept_records = await dept_service. list_depts_by_ids(dept_ids)
        # 构建id -> name 映射
        dept_map = {item.id: item.dept_name for item in dept_records}
    else:
        dept_map = {}

    # 2. 内存循环赋值，无DB查询
    for post in post_list:
        post.dept_name = dept_map.get(post.dept_id, "")
    return ResponseBuilder.pagination(post_list, total, query.page_num, query.page_size)


@router.get(
    "/{post_id}",
    response_model=ApiResponse[PostInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Post.READ))],
    summary="获取岗位详情",
    description="根据岗位ID获取岗位详情"
)
async def get_post_info(
    post_id: int = Path(..., description="岗位ID", ge=1),
    post_service: PostService = Depends(get_post_service),
):
    """
    获取岗位详情

    根据岗位ID获取岗位详情。
    接口需要用户登录并拥有岗位读取权限方可访问。

    :param post_id: 岗位ID
    :return: 返回岗位详情
    :raises BusinessError: 岗位不存在
    """
    post = await post_service.get_post(post_id)
    return ResponseBuilder.success(post)


@router.post(
    "",
    response_model=ApiResponse[PostInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Post.CREATE))],
    summary="创建岗位",
    description="创建新岗位"
)
async def create_post(
    req: PostCreateRequest = Body(..., description="创建岗位请求"),
    post_service: PostService = Depends(get_post_service)
):
    """
    创建岗位

    创建新岗位，要求岗位名称和岗位编码唯一。
    接口需要用户登录并拥有岗位创建权限方可访问。

    :param req: 创建岗位请求
    :return: 返回创建后的岗位详情
    :raises BusinessError: 岗位名称已存在 / 岗位编码已存在
    """
    post = await post_service.create_post(req)
    return ResponseBuilder.success(post)


@router.put(
    "",
    response_model=ApiResponse[PostInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Post.UPDATE))],
    summary="编辑岗位",
    description="更新岗位信息"
)
async def update_post(
    req: PostUpdateRequest = Body(..., description="编辑岗位请求"),
    post_service: PostService = Depends(get_post_service)
):
    """
    编辑岗位

    根据岗位ID更新岗位信息，要求岗位名称和岗位编码唯一（排除自身）。
    接口需要用户登录并拥有岗位更新权限方可访问。

    :param req: 编辑岗位请求
    :return: 返回更新后的岗位详情
    :raises BusinessError: 岗位不存在 / 岗位名称已存在 / 岗位编码已存在
    """
    post = await post_service.update_post(req)
    return ResponseBuilder.success(post)


@router.delete(
    "/batch",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Post.DELETE))],
    summary="批量删除岗位",
    description="批量删除岗位"
)
async def batch_delete_post(
    req: PostBatchDeleteRequest = Body(..., description="批量删除岗位请求"),
    post_service: PostService = Depends(get_post_service)
):
    """
    批量删除岗位

    批量删除岗位。
    接口需要用户登录并拥有岗位删除权限方可访问。

    :param req: 批量删除岗位请求
    :return: 无返回数据
    :raises BusinessError: 岗位不存在
    """
    await post_service.batch_delete_post(req.post_ids)
    return ResponseBuilder.success()


@router.delete(
    "/{post_id}",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Post.DELETE))],
    summary="删除岗位",
    description="删除岗位"
)
async def delete_post(
    post_id: int = Path(..., description="岗位ID", ge=1),
    post_service: PostService = Depends(get_post_service)
):
    """
    删除岗位

    删除岗位。
    接口需要用户登录并拥有岗位删除权限方可访问。

    :param post_id: 岗位ID
    :return: 无返回数据
    :raises BusinessError: 岗位不存在
    """
    await post_service.delete_post(post_id)
    return ResponseBuilder.success()


@router.get(
    "/{post_id}/roles",
    response_model=ApiResponse[list[int]],
    dependencies=[Depends(has_perm(PermCode.Post.READ))],
    summary="获取岗位角色列表",
    description="获取指定岗位已分配的角色ID列表"
)
async def get_post_roles(
    post_id: int = Path(..., description="岗位ID", ge=1),
    post_service: PostService = Depends(get_post_service)
):
    """
    获取岗位角色列表

    获取指定岗位已分配的角色ID列表。
    接口需要用户登录并拥有岗位读取权限方可访问。

    :param post_id: 岗位ID
    :return: 角色ID列表
    :raises BusinessError: 岗位不存在
    """
    roles = await post_service.get_posts_bind_roles([post_id])
    return ResponseBuilder.success([role.id for role in roles])


@router.post(
    "/{post_id}/roles/assign",
    response_model=ApiResponse[list[int]],
    dependencies=[Depends(has_perm(PermCode.Post.UPDATE))],
    summary="分配岗位角色",
    description="对比差异分配岗位角色：新增没有的、删除多余的、保留共有的（需要具备岗位编辑权限）"
)
async def assign_post_roles(
    post_id: int = Path(..., description="岗位ID", ge=1),
    req: PostRoleAssignRequest = Body(..., description="角色分配请求"),
    post_service: PostService = Depends(get_post_service)
):
    """
    分配岗位角色（智能合并）

    工作逻辑：
    1. 前端传入岗位调整后的所有角色ID
    2. 后端对比数据库中已有的角色
    3. 数据库没有，前端有 → 新增关联
    4. 数据库有，前端没有 → 删除关联
    5. 两边都有 → 保持不变

    特点：
    - 只变更有差异的记录，不影响无变化的角色
    - 前端无需关心哪些是新增、哪些是删除
    - 传入空列表 [] = 清空所有角色

    接口需要用户登录并拥有岗位编辑权限方可访问。

    :param post_id: 岗位ID
    :param req: 最终的角色ID列表
    :return: 返回分配后的角色ID列表
    :raises BusinessError: 岗位不存在
    """
    role_ids = await post_service.assign_roles_to_post(post_id, req.role_ids)
    return ResponseBuilder.success(role_ids)
