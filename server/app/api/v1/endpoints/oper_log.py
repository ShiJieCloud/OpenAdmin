from fastapi import APIRouter, Depends, Body

from app.core.enums import PermCode
from app.core.response import ResponseBuilder
from app.deps.permission import has_perm
from app.deps.service import get_oper_log_service
from app.schemas.base.response import PaginationResponse
from app.schemas import OperLogResponse, OperLogListQueryRequest
from app.services import OperLogService

router = APIRouter()


@router.post(
    "/list",
    response_model=PaginationResponse[OperLogResponse],
    dependencies=[Depends(has_perm(PermCode.OperLog.LIST))],
    summary="分页查询操作日志列表",
    description="分页获取操作日志列表，支持多条件筛选（需要具备操作日志查看权限）"
)
async def get_oper_log_list(
    query: OperLogListQueryRequest = Body(..., description="查询条件"),
    oper_log_service: OperLogService = Depends(get_oper_log_service)
):
    """
    分页查询操作日志列表

    支持的条件筛选：
    - 链路追踪ID（精确匹配）
    - HTTP请求方法（精确匹配）
    - API接口路径（模糊查询）
    - API接口名称（模糊查询）
    - 业务模块（精确匹配）
    - 操作员ID（精确匹配）
    - 客户端IP（模糊查询）
    - 响应码（精确匹配）
    - 时间范围（开始时间-结束时间）

    结果按操作时间倒序排列。
    接口需要用户登录并拥有操作日志查看权限方可访问。

    :param query: 分页参数和筛选条件
    :return: 返回分页操作日志列表
    """
    logs, total, pages, page_num = await oper_log_service.get_oper_log_list(query)
    records = [OperLogResponse.model_validate(log) for log in logs]
    return ResponseBuilder.pagination(records, total, page_num, query.page_size)