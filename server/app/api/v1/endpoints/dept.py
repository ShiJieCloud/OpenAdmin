from fastapi import APIRouter, Depends, Path, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_dept_service
from app.schemas.base.response import ApiResponse
from app.schemas.dept import DeptInfoResponse, DeptCreateRequest, DeptUpdateRequest, DeptBatchDeleteRequest
from app.services import DeptService
router = APIRouter()


@router.get(
    "/list",
    response_model=ApiResponse[list[DeptInfoResponse]],
    dependencies=[Depends(has_perm(PermCode.Dept.LIST))],
    summary="获取部门列表",
    description="获取部门列表（需要具备部门列表查询权限）"
)
async def get_dept_list(
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    获取部门列表

    返回所有部门的列表。
    接口需要用户登录并拥有部门列表查询权限方可访问。

    :param status: 状态筛选（可选）
    :return: 返回部门列表
    """
    dept_list = await dept_service.get_dept_list()
    return ResponseBuilder.success(dept_list)


@router.get(
    "/{dept_id}",
    response_model=ApiResponse[DeptInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Dept.GET))],
    summary="获取部门详情",
    description="根据部门唯一ID查询指定部门的详细信息（需要具备部门详情查询权限）"
)
async def get_dept_info(
    dept_id: int = Path(..., description="部门ID", ge=1, examples=[1]),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    获取部门详情

    根据部门ID查询部门完整信息，包括部门名称、父级ID、排序、状态等，
    接口需要用户登录并拥有部门详情查询权限方可访问。

    :param dept_id: 目标部门的唯一标识ID
    :return: 返回部门详细信息
    :raises BusinessError: 部门不存在
    """
    dept = await dept_service.get_dept(dept_id)
    return ResponseBuilder.success(dept)


@router.post(
    "",
    response_model=ApiResponse[DeptInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Dept.CREATE))],
    summary="创建部门",
    description="创建新部门（需要具备部门创建权限）"
)
async def create_dept(
    req: DeptCreateRequest = Body(..., description="创建部门请求"),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    创建部门

    创建新部门，要求同级部门名称唯一，父级部门必须存在。
    接口需要用户登录并拥有部门创建权限方可访问。

    :param req: 创建部门信息
    :return: 返回创建后的部门详情
    :raises BusinessError: 同级部门名称已存在 / 父级部门不存在
    """
    dept = await dept_service.create_dept(req)
    return ResponseBuilder.success(dept)


@router.put(
    "",
    response_model=ApiResponse[DeptInfoResponse],
    dependencies=[Depends(has_perm(PermCode.Dept.UPDATE))],
    summary="编辑部门",
    description="更新部门信息（需要具备部门编辑权限）"
)
async def update_dept(
    req: DeptUpdateRequest = Body(..., description="编辑部门请求"),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    编辑部门

    根据部门ID更新部门信息，包括部门名称、父级ID、排序、状态等，
    同级部门名称必须唯一（排除自身）。
    接口需要用户登录并拥有部门编辑权限方可访问。

    :param req: 编辑部门信息
    :return: 返回更新后的部门详情
    :raises BusinessError: 部门不存在 / 同级部门名称已存在 / 父级部门不能是自身
    """
    dept = await dept_service.update_dept(req)
    return ResponseBuilder.success(dept)


@router.delete(
    "/batch",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Dept.DELETE))],
    summary="批量删除部门",
    description="批量删除部门（需要具备部门删除权限）"
)
async def batch_delete_dept(
    req: DeptBatchDeleteRequest = Body(..., description="批量删除部门请求"),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    批量删除部门

    批量物理删除部门，存在子部门时无法删除。
    接口需要用户登录并拥有部门删除权限方可访问。

    :param req: 批量删除部门请求，包含部门ID列表
    :return: 无返回数据
    :raises BusinessError: 部门不存在 / 部门存在子部门
    """
    await dept_service.batch_delete_dept(req.dept_ids)
    return ResponseBuilder.success()


@router.delete(
    "/{dept_id}",
    response_model=ApiResponse[None],
    dependencies=[Depends(has_perm(PermCode.Dept.DELETE))],
    summary="删除部门",
    description="删除部门（需要具备部门删除权限）"
)
async def delete_dept(
    dept_id: int = Path(..., description="部门ID", ge=1, examples=[1]),
    dept_service: DeptService = Depends(get_dept_service)
):
    """
    删除部门

    物理删除部门，存在子部门时无法删除。
    接口需要用户登录并拥有部门删除权限方可访问。

    :param dept_id: 要删除的部门ID
    :return: 无返回数据
    :raises BusinessError: 部门不存在 / 部门存在子部门
    """
    await dept_service.delete_dept(dept_id)
    return ResponseBuilder.success()
