from fastapi import APIRouter, Depends, Path, Body, Query

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_user_apply_service
from app.schemas.base.response import ApiResponse, PaginationResponse
from app.schemas.user_apply import (
    UserApplyListQueryRequest,
    UserApplyRejectRequest,
    UserApplyPassRequest,
    UserApplyInfoResponse,
)
from app.services import UserApplyService

router = APIRouter()


@router.get(
    "/user-register-apply/list",
    response_model=PaginationResponse[UserApplyInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.VIEW))],
    summary="获取注册申请列表",
    description="分页查询用户注册申请列表，支持多条件筛选（需要具备用户查看权限）"
)
async def get_user_apply_list(
    page_num: int = Query(1, description="当前页码", ge=1, example=1),
    page_size: int = Query(10, description="每页条数", ge=1, le=100, example=10),
    username: str | None = Query(None, description="登录账号（模糊查询）", max_length=50),
    phone: str | None = Query(None, description="手机号（模糊查询）", max_length=20),
    status: int | None = Query(None, description="审核状态：0=待审核 1=已通过 2=已拒绝 3=撤销", ge=0, le=3),
    apply_service: UserApplyService = Depends(get_user_apply_service)
):
    """
    分页查询用户注册申请列表

    支持的条件筛选：
    - 用户名、手机号（模糊查询）
    - 审核状态（精确匹配）

    结果按创建时间倒序排列。
    接口需要用户登录并拥有用户查看权限方可访问。

    :return: 返回分页申请列表
    """
    query = UserApplyListQueryRequest(
        page_num=page_num,
        page_size=page_size,
        username=username,
        phone=phone,
        status=status,
    )

    records, total, _, page_num = await apply_service.get_apply_list(query)

    data = [UserApplyInfoResponse.model_validate(apply) for apply in records]
    return ResponseBuilder.pagination(data, total, page_num, query.page_size)


@router.get(
    "/user-register-apply/{apply_id}",
    response_model=ApiResponse[UserApplyInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.VIEW))],
    summary="获取注册申请详情",
    description="根据申请ID查询用户注册申请的详细信息（需要具备用户查看权限）"
)
async def get_user_apply_info(
    apply_id: int = Path(..., description="申请ID", ge=1, examples=[1001]),
    apply_service: UserApplyService = Depends(get_user_apply_service)
):
    """
    获取注册申请详情

    根据申请ID查询用户注册申请完整信息，包括基础信息、审批信息等。
    接口需要用户登录并拥有用户查看权限方可访问。

    :param apply_id: 申请ID
    :return: 返回申请详细信息
    :raises BusinessError: 申请不存在
    """
    apply = await apply_service.get_apply(apply_id)
    apply_info = UserApplyInfoResponse.model_validate(apply)
    return ResponseBuilder.success(apply_info)


@router.post(
    "/user-register-apply/{apply_id}/pass",
    response_model=ApiResponse[UserApplyInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.CREATE))],
    summary="审批通过",
    description="通过指定用户注册申请，同时创建对应系统用户并绑定部门/岗位（需要具备用户创建权限）"
)
async def pass_user_apply(
    apply_id: int = Path(..., description="申请ID", ge=1, examples=[1001]),
    req: UserApplyPassRequest = Body(..., description="审批通过请求，包含部门ID和岗位ID列表"),
    apply_service: UserApplyService = Depends(get_user_apply_service)
):
    """
    审批通过

    通过指定用户注册申请，同时会创建对应系统用户记录，用户状态默认正常，
    并根据上送的部门ID和岗位ID列表完成用户-部门归属和岗位绑定。
    岗位必须全部属于上送部门，否则拒绝。
    该操作在数据库事务内完成（创建用户 + 绑定岗位 + 更新申请状态）。
    接口需要用户登录并拥有用户创建权限方可访问。

    :param apply_id: 申请ID
    :param req: 审批通过请求，包含部门ID和岗位ID列表
    :return: 返回更新后的申请详细信息
    :raises BusinessError: 申请不存在、申请已处理、用户名/手机号已被占用、
                          岗位不存在、岗位部门与上送部门不一致
    """
    apply = await apply_service.pass_apply(apply_id, req)
    apply_info = UserApplyInfoResponse.model_validate(apply)
    return ResponseBuilder.success(apply_info, message="审批通过成功")


@router.post(
    "/user-register-apply/{apply_id}/reject",
    response_model=ApiResponse[UserApplyInfoResponse],
    dependencies=[Depends(has_perm(PermCode.User.UPDATE))],
    summary="审批拒绝",
    description="拒绝指定用户注册申请，记录拒绝原因（需要具备用户更新权限）"
)
async def reject_user_apply(
    apply_id: int = Path(..., description="申请ID", ge=1, examples=[1001]),
    req: UserApplyRejectRequest = Body(..., description="拒绝请求，包含拒绝原因"),
    apply_service: UserApplyService = Depends(get_user_apply_service)
):
    """
    审批拒绝

    拒绝指定用户注册申请，并记录拒绝原因。
    接口需要用户登录并拥有用户更新权限方可访问。

    :param apply_id: 申请ID
    :param req: 拒绝请求，包含拒绝原因
    :return: 返回更新后的申请详细信息
    :raises BusinessError: 申请不存在、申请已处理
    """
    apply = await apply_service.reject_apply(apply_id, req)
    apply_info = UserApplyInfoResponse.model_validate(apply)
    return ResponseBuilder.success(apply_info, message="审批拒绝成功")
