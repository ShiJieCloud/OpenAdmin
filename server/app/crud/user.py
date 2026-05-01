from typing import List
from sqlalchemy import select
from sqlalchemy.sql.functions import count

from app.crud.base import BaseCRUD
from app.models.user import User


class UserCRUD(BaseCRUD):
    """用户 CRUD 操作类"""

    async def get_user(self, 
        id: int | None = None,
        username: str | None = None,
        email: str | None = None,
        phone: str | None = None
    ) -> User | None:
        """根据 ID、用户名、邮箱或手机号获取用户
        
        Args:
            id: 用户 ID
            username: 用户名
            email: 邮箱
            phone: 手机号
            
        Returns:
            用户对象或 None 如果未找到匹配用户
        """

        # 1. 至少传入一个查询条件
        if all([id is None, not username, not email, not phone]):
            return None

        # 2. 构建查询条件
        conditions = []
        if id is not None:
            conditions.append(User.id == id)
        if username is not None:
            conditions.append(User.username == username)
        if email is not None:
            conditions.append(User.email == email)
        if phone is not None:
            conditions.append(User.phone == phone)

        query_stmt = select(User).where(*conditions)

        # 3. 执行查询
        result = await self.db_session.execute(query_stmt)
        return result.scalar_one_or_none()
