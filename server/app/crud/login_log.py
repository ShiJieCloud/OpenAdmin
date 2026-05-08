from math import ceil
from sqlalchemy import select, func

from app.crud.base import BaseCRUD
from app.models import LoginLog
from app.schemas.login_log import LoginLogListQueryRequest


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
        
        if query.operate_type is not None:
            conditions.append(LoginLog.operate_type == query.operate_type)
        
        if query.login_type is not None:
            conditions.append(LoginLog.login_type == query.login_type)
        
        if query.login_status is not None:
            conditions.append(LoginLog.login_status == query.login_status)
        
        if query.login_ip:
            conditions.append(LoginLog.login_ip.like(f"%{query.login_ip}%"))
        
        if query.start_time:
            conditions.append(LoginLog.operate_time >= query.start_time)
        
        if query.end_time:
            conditions.append(LoginLog.operate_time <= query.end_time)

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
            .order_by(LoginLog.operate_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        logs = list(list_result.scalars().all())

        return logs, total, pages, query.page_num
