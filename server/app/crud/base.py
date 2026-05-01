from sqlalchemy.ext.asyncio import AsyncSession


class BaseCRUD:
    """基础 CRUD 类"""

    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session