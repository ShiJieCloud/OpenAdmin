from math import ceil
from datetime import datetime
from sqlalchemy import select, func

from app.crud.base import BaseCRUD
from app.models import OperLog


class OperLogCRUD(BaseCRUD):
    """操作日志 CRUD 操作类"""

    async def create_oper_log(self, data: dict) -> None:
        """
        创建操作日志

        :param data: 操作日志数据
        :return: None
        """
        oper_log = OperLog(**data)
        self.db_session.add(oper_log)
        await self.db_session.flush()

    async def get_oper_log_list(
        self,
        oper_log: OperLog,
        page_num: int = 1,
        page_size: int = 10,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> tuple[list[OperLog], int, int, int]:
        """
        分页查询操作日志列表

        :param page_num: 当前页码
        :param page_size: 每页条数
        :param trace_id: 链路追踪ID（精确匹配）
        :param request_method: HTTP请求方法（精确匹配）
        :param api_path: API接口路径（模糊查询）
        :param api_name: API接口名称（模糊查询）
        :param module: 业务模块（精确匹配）
        :param operator_id: 操作员ID（精确匹配）
        :param client_ip: 客户端IP（模糊查询）
        :param response_code: 响应码（精确匹配）
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return: (日志列表, 总条数, 总页数, 当前页码)
        """
        conditions = []

        if oper_log.trace_id:
            conditions.append(OperLog.trace_id == oper_log.trace_id)

        if oper_log.request_method:
            conditions.append(OperLog.request_method == oper_log.request_method)

        if oper_log.api_path:
            conditions.append(OperLog.api_path.like(f"%{_path}%"))

        if oper_log.api_name:
            conditions.append(OperLog.api_name.like(f"%{oper_log.api_name}%"))

        if oper_log.module:
            conditions.append(OperLog.module == oper_log.module)

        if oper_log.operator_id:
            conditions.append(OperLog.operator_id == oper_log.operator_id)

        if oper_log.client_ip:
            conditions.append(OperLog.client_ip.like(f"%{oper_log.client_ip}%"))

        if oper_log.response_code:
            conditions.append(OperLog.response_code == oper_log.response_code)

        if start_time:
            conditions.append(OperLog.create_time >= start_time)

        if end_time:
            conditions.append(OperLog.create_time <= end_time)

        count_stmt = select(func.count(OperLog.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        pages = ceil(total / page_size) if total > 0 else 1

        offset = (page_num - 1) * page_size
        list_stmt = (
            select(OperLog)
            .where(*conditions)
            .order_by(OperLog.create_time.desc())
            .offset(offset)
            .limit(page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        logs = list(list_result.scalars().all())
        return logs, total, pages, page_num
