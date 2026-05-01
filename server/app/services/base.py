from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    """
    Service 基类：
    1. 封装数据库会话的注入
    """
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session