from fastapi import APIRouter, Depends, Path, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_login_log_service
from app.schemas.base.response import ApiResponse, PaginationResponse
from app.schemas.login_log import LoginLogResponse, LoginLogListQueryRequest
from app.services import LoginLogService

router = APIRouter()


@router.post(
    "/list",
    response_model=PaginationResponse[LoginLogResponse],
    dependencies=[Depends(has_perm(PermCode.Log.READ))],
    summary="分页查询登录日志列表",
    description="分页获取登录日志列表，支持多条件筛选（需要具备日志查看权限）"
)
async def get_login_log_list(
    query: LoginLogListQueryRequest = Body(..., description="查询条件"),
    login_log_service: LoginLogService = Depends(get_login_log_service)
):
    """
    分页查询登录日志列表
    
    支持的条件筛选：
    - 用户ID（精确匹配）
    - 登录账号（模糊查询）
    - 操作类型（精确匹配：1-登录 2-登出）
    - 登录类型（精确匹配：1-账号密码 2-短信 3-第三方 4-扫码 5-邮箱）
    - 登录状态（精确匹配：0-成功 1-失败）
    - 登录IP（模糊查询）
    - 时间范围（开始时间-结束时间）
    
    结果按操作时间倒序排列。
    接口需要用户登录并拥有日志查看权限方可访问。
    
    :param query: 分页参数和筛选条件
    :return: 返回分页登录日志列表
    """
    logs, total, pages, page_num = await login_log_service.get_login_log_list(query)
    records = [LoginLogResponse.model_validate(log) for log in logs]
    return ResponseBuilder.pagination(records, total, page_num, query.page_size)