from fastapi import APIRouter, Depends, Path, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_user_service
from app.schemas.base.response import ApiResponse, PaginationResponse
from app.schemas.user import UserInfoResponse, UserCreateRequest, UserResetPasswordRequest, UserUpdateStatusRequest, UserUpdateRequest, UserListQueryRequest, UserRoleAssignRequest
from app.services import UserService

router = APIRouter()


@router.get(
    "/{user_id}",
    response_model=ApiResponse[UserInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.READ))],
    summary="获取用户详情",
    description="根据用户唯一ID查询指定用户的详细信息（需要具备用户查看权限）"
)
async def get_user_info(
    user_id: int = Path(..., description="用户ID", ge=1, examples=[1001]),
    user_service: UserService = Depends(get_user_service)
):
    """
    获取用户详情
    
    根据用户ID查询用户完整信息，包括基础信息、状态等，
    接口需要用户登录并拥有用户查看权限方可访问。
    
    :param user_id: 目标用户的唯一标识ID
    :return: 返回用户详细信息
    :raises BusinessError: 用户不存在
    """
    user = await user_service.get_user(user_id)
    user_info = UserInfoResponse.model_validate(user)
    return ResponseBuilder.success(user_info)


@router.post(
    "",
    response_model=ApiResponse[UserInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.CREATE))],
    summary="创建用户",
    description="创建新用户账号（需要具备用户创建权限）"
)
async def create_user(
    req: UserCreateRequest = Body(..., description="创建用户请求信息"),
    user_service: UserService = Depends(get_user_service)
):
    """
    创建新用户
    
    :param req: 创建用户请求信息
    :return: 返回创建后的用户详细信息
    :raises BusinessError: 用户名/邮箱/手机号已存在
    """
    user = await user_service.create_user(req)
    user_info = UserInfoResponse.model_validate(user)
    return ResponseBuilder.success(user_info)


@router.post(
    "/reset-password",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.User.RESET_PASSWORD))],
    summary="重置用户密码",
    description="重置指定用户的登录密码（需要具备用户重置密码权限）"
)
async def reset_user_password(
    req: UserResetPasswordRequest = Body(..., description="重置密码请求信息"),
    user_service: UserService = Depends(get_user_service)
):
    """
    重置用户密码
    
    管理员重置指定用户的登录密码。
    接口需要用户登录并拥有用户重置密码权限方可访问。
    
    :param req: 重置密码请求信息，包含用户ID和新密码
    :return: 返回成功响应
    :raises BusinessError: 用户不存在
    """
    await user_service.reset_user_password(req)
    return ResponseBuilder.success()


@router.put(
    "/status",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.User.UPDATE))],
    summary="修改用户状态",
    description="修改用户账号状态（启用/禁用/冻结，需要具备用户更新权限）"
)
async def update_user_status(
    req: UserUpdateStatusRequest = Body(..., description="修改用户状态请求信息"),
    user_service: UserService = Depends(get_user_service)
):
    """
    修改用户状态
    
    管理员修改用户账号状态，支持启用、禁用、冻结操作。
    接口内置完整的状态互斥和拦截规则：
    - 用户已注销时拒绝任何状态修改
    - 禁止手动设置为登录锁定或注销状态
    - 校验状态流转的合法性
    
    接口需要用户登录并拥有用户更新权限方可访问。
    
    :param req: 修改用户状态请求信息，包含用户ID和目标状态
    :return: 返回成功响应
    :raises BusinessError: 用户不存在、用户已注销、状态无需修改、不支持的状态流转
    """
    await user_service.update_user_status(req)
    return ResponseBuilder.success()


@router.put(
    "",
    response_model=ApiResponse[UserInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.UPDATE))],
    summary="编辑用户基础信息",
    description="编辑用户基础信息（需要具备用户更新权限）"
)
async def update_user_info(
    req: UserUpdateRequest = Body(..., description="编辑用户信息请求"),
    user_service: UserService = Depends(get_user_service)
):
    """
    编辑用户基础信息
    
    更新用户的昵称、头像、邮箱、手机号、性别、所属部门、备注等信息。
    接口会自动校验邮箱和手机号的唯一性（排除当前用户）。
    接口需要用户登录并拥有用户更新权限方可访问。
    
    :param req: 编辑用户信息请求
    :return: 返回更新后的用户详细信息
    :raises BusinessError: 用户不存在、邮箱已存在、手机号已存在
    """
    user = await user_service.update_user_info(req)
    user_info = UserInfoResponse.model_validate(user)
    return ResponseBuilder.success(user_info)


@router.post(
    "/list",
    response_model=PaginationResponse[UserInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.READ))],
    summary="分页查询用户列表",
    description="分页获取用户列表，支持多条件筛选（需要具备用户查看权限）"
)
async def get_user_list(
    query: UserListQueryRequest = Body(..., description="查询条件"),
    user_service: UserService = Depends(get_user_service)
):
    """
    分页查询用户列表
    
    支持的条件筛选：
    - 用户名、昵称、邮箱、手机号（模糊查询）
    - 账号状态（精确匹配）
    - 所属部门ID（精确匹配）
    
    结果按创建时间倒序排列。
    接口需要用户登录并拥有用户查看权限方可访问。
    
    :param query: 分页参数和筛选条件
    :return: 返回分页用户列表
    """
    users, total, pages, page_num = await user_service.get_user_list(query)
    records = [UserInfoResponse.model_validate(user) for user in users]
    return ResponseBuilder.pagination(records, total, page_num, query.page_size)


@router.post(
    "/roles/assign",
    response_model=ApiResponse[list[int]],
    dependencies=[Depends(has_perm(PermCode.User.UPDATE))],
    summary="分配用户角色",
    description="对比差异分配用户角色：新增没有的、删除多余的、保留共有的（需要具备用户编辑权限）"
)
async def assign_user_roles(
    req: UserRoleAssignRequest = Body(..., description="角色分配请求"),
    user_service: UserService = Depends(get_user_service)
):
    """
    分配用户角色（智能合并）

    工作逻辑：
    1. 前端传入用户调整后的所有角色ID
    2. 后端对比数据库中已有的角色
    3. 数据库没有，前端有 → 新增关联
    4. 数据库有，前端没有 → 删除关联
    5. 两边都有 → 保持不变

    特点：
    - 只变更有差异的记录，不影响无变化的角色
    - 前端无需关心哪些是新增、哪些是删除
    - 传入空列表 [] = 清空所有角色

    接口需要用户登录并拥有用户编辑权限方可访问。

    :param req: 用户ID和最终的角色ID列表
    :return: 返回分配后的角色ID列表
    :raises BusinessError: 用户不存在
    """
    role_ids = await user_service.assign_roles_to_user(req.user_id, req.role_ids)
    return ResponseBuilder.success(role_ids)
