from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import LoginLogCRUD
from app.models import LoginLog
from app.schemas.login_log import LoginLogListQueryRequest
from app.services.base import BaseService


class LoginLogService(BaseService):
    """登录日志服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.login_log_crud = LoginLogCRUD(db_session)

    async def get_login_log_list(self, query: LoginLogListQueryRequest) -> tuple[list[LoginLog], int, int, int]:
        """
        分页查询登录日志列表

        :param query: 查询条件
        :return: (日志列表, 总条数, 总页数, 当前页码)
        """
        logs, total, pages, page_num = await self.login_log_crud.get_login_log_list(query)
        return logs, total, pages, page_num
