from app.crud import LoginLogCRUD
from app.models import LoginLog
from app.schemas import LoginLogListQueryRequest, LoginLogCreateRequest, LoginLogResponse
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

    async def paginate_login_logs(self, query: LoginLogListQueryRequest) -> tuple[list[LoginLog], int, int, int]:
        """
        分页查询登录日志列表

        :param query: 查询条件（Pydantic schema）
        :return: (日志列表, 总条数, 总页数, 当前页码)
        """
        # 将 Pydantic schema 转换为 LoginLog 模型实例
        query_data = query.model_dump(exclude_unset=True, exclude={"start_time", "end_time", "page_num", "page_size"})
        
        login_log_query = LoginLog(**query_data)
        
        return await self.login_log_crud.paginate_login_logs(
            query=login_log_query,
            start_time=query.start_time,
            end_time=query.end_time,
            page_num=query.page_num,
            page_size=query.page_size
        )

    async def get_recent_login_logs(self, limit: int = 10) -> list[LoginLogResponse]:
        """
        获取最近登录日志

        :param limit: 每页返回条数，默认10条
        :return: 最近登录日志列表
        """
        # 创建空的查询条件实例
        empty_query = LoginLog()
        
        logs, _, _, _ = await self.login_log_crud.paginate_login_logs(empty_query)
        return [LoginLogResponse.model_validate(login_log) for login_log in logs]
