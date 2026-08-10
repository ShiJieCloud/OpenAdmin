from datetime import datetime
from math import ceil

from sqlalchemy import select, func

from app.crud.base import BaseCRUD
from app.models import LoginLog


class LoginLogCRUD(BaseCRUD):
    """登录日志 CRUD 操作类"""

    async def paginate_login_logs(
        self,
        query: LoginLog,
        start_time: datetime = None,
        end_time: datetime = None,
        page_num: int = 1,
        page_size: int = 10,
    ) -> tuple[list[LoginLog], int, int, int]:
        """
        分页查询登录日志列表

        :param query: 查询条件（LoginLog 模型实例，非空字段作为过滤条件）
        :param page_num: 当前页码，默认1
        :param page_size: 每页返回条数，默认10条
        :return: (日志列表, 总条数, 总页数, 当前页)
        """
        # 构建查询条件
        conditions = []

        if query.user_id:
            conditions.append(LoginLog.user_id == query.user_id)

        if query.username:
            conditions.append(LoginLog.username.like(f"%{query.username}%"))

        if query.response_code:
            conditions.append(LoginLog.response_code == query.response_code)

        if query.client_ip:
            conditions.append(LoginLog.client_ip.like(f"%{query.client_ip}%"))

        if query.os:
            conditions.append(LoginLog.os.like(f"%{query.os}%"))

        if query.browser:
            conditions.append(LoginLog.browser.like(f"%{query.browser}%"))

        if query.ip_country:
            conditions.append(LoginLog.ip_country.like(f"%{query.ip_country}%"))

        if query.ip_province:
            conditions.append(LoginLog.ip_province.like(f"%{query.ip_province}%"))

        if query.ip_city:
            conditions.append(LoginLog.ip_city.like(f"%{query.ip_city}%"))

        if start_time:
            conditions.append(LoginLog.create_time >= start_time)

        if end_time:
            conditions.append(LoginLog.create_time <= end_time)

        # 查询总条数
        count_stmt = select(func.count(LoginLog.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        # 计算总页数
        pages = ceil(total / page_size) if total > 0 else 1

        # 分页查询登录日志列表，按操作时间倒序
        offset = (page_num - 1) * page_size
        list_stmt = (
            select(LoginLog)
            .where(*conditions)
            .order_by(LoginLog.create_time.desc())
            .offset(offset)
            .limit(page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        logs = list(list_result.scalars().all())
        return logs, total, pages, page_num

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

