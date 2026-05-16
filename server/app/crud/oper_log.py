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
