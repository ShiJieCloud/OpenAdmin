from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import LoginLogCRUD
from app.models import LoginLog
from app.schemas import LoginLogListQueryRequest, LoginLogCreateRequest
from app.services.base import BaseService


class LoginLogService(BaseService):
    """登录日志服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.login_log_crud = LoginLogCRUD(db_session)
    async def create_login_log(self, login_log: LoginLogCreateRequest) -> LoginLog:
        """
        创建登录日志

        :param login_log: 登录日志对象
        :return: 创建后的登录日志对象
        """
        login_log_data = login_log.model_dump()
        return await self.login_log_crud.create_login_log(login_log_data)



    async def get_login_log_list(self, query: LoginLogListQueryRequest) -> tuple[list[LoginLog], int, int, int]:
        """
        分页查询登录日志列表

        :param query: 查询条件
        :return: (日志列表, 总条数, 总页数, 当前页码)
        """
        query = query.model_dump(exclude_unset=True)
        login_log = LoginLog(
            trace_id=query.trace_id,
            request_method=query.request_method,
            api_path=query.api_path,
            api_name=query.api_name,
            module=query.module,
            operator_id=query.operator_id,
            client_ip=query.client_ip,
            response_code=query.response_code,
        )
        logs, total, pages, page_num = await self.login_log_crud.get_login_log_list(
                login_log,
                query.page_num,
                query.page_size,
                query.start_time,
                query.end_time,
            )
        return logs, total, pages, page_num
