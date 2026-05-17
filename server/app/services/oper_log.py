from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import OperLogCRUD
from app.models import OperLog
from app.schemas import OperLogCreateRequest, OperLogListQueryRequest
from app.services.base import BaseService


class OperLogService(BaseService):
    """操作日志服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.oper_log_crud = OperLogCRUD(db_session)

    async def create_oper_log(self, data: OperLogCreateRequest) -> None:
        """
        创建操作日志

        :param data: 操作日志数据
        :return: None
        """
        if not data:
            raise BusinessError(RespCodeEnum.PARAM_ERROR, "操作日志数据不能为空")

        log_data = data.model_dump()
        await self.oper_log_crud.create_oper_log(log_data)

    async def get_oper_log_list(self, query: OperLogListQueryRequest) -> tuple[list[OperLog], int, int, int]:
        """
        分页查询操作日志列表

        :param query: 查询条件
        :return: (日志列表, 总条数, 总页数, 当前页码)
        """
        oper_log = OperLog(
            trace_id=query.trace_id,
            request_method=query.request_method,
            api_path=query.api_path,
            api_name=query.api_name,
            module=query.module,
            operator_id=query.operator_id,
            client_ip=query.client_ip,
            response_code=query.response_code,
        )
        logs, total, pages, page_num = await self.oper_log_crud.get_oper_log_list(
                oper_log,
                query.page_num,
                query.page_size,
                query.start_time,
                query.end_time,
            )
        return logs, total, pages, page_num