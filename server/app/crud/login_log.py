from math import ceil
from sqlalchemy import select, func

from app.crud.base import BaseCRUD
from app.models import LoginLog
from app.schemas.login_log import LoginLogCreateRequest, LoginLogListQueryRequest


class LoginLogCRUD(BaseCRUD):
    """登录日志 CRUD 操作类"""

    async def get_login_log_list(self, query: LoginLogListQueryRequest) -> tuple[list[LoginLog], int, int, int]:
        """
        分页查询登录日志列表

        :param query: 查询条件
        :return: (日志列表, 总条数, 总页数, 当前页)
        """
        # 构建查询条件
        conditions = []

        if query.user_id:
            conditions.append(LoginLog.user_id == query.user_id)
        
        if query.username:
            conditions.append(LoginLog.username.like(f"%{query.username}%"))
        
        if query.client_ip:
            conditions.append(LoginLog.client_ip.like(f"%{query.client_ip}%"))
        
        if query.start_time:
            conditions.append(LoginLog.create_time >= query.start_time)
        
        if query.end_time:
            conditions.append(LoginLog.create_time <= query.end_time)

        # 查询总条数
        count_stmt = select(func.count(LoginLog.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        # 计算总页数
        pages = ceil(total / query.page_size) if total > 0 else 1

        # 分页查询登录日志列表，按操作时间倒序
        offset = (query.page_num - 1) * query.page_size
        list_stmt = (
            select(LoginLog)
            .where(*conditions)
            .order_by(LoginLog.create_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        logs = list(list_result.scalars().all())
        return logs, total, pages, query.page_num

    async def create_login_log(self, login_log: dict) -> LoginLog:
        """
        创建登录日志记录

        :param login_log: 登录日志创建请求对象
        :return: 创建后的登录日志对象
        """
        if not login_log:
            return None
        login_log = LoginLog(**login_log)
        self.db_session.add(login_log)
        await self.db_session.flush()
        await self.db_session.refresh(login_log)
        return login_log

