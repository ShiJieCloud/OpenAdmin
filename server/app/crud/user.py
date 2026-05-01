from datetime import datetime
from sqlalchemy import select, update

from app.core.enums import UserStatusEnum
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

    async def increment_login_fail_count(self, user_id: int) -> None:
        """
        修改登录失败次数

        :param user_id: 用户 ID
        :param fail_count: 失败次数，默认1次
        :return: None
        """

        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(login_fail_count=User.login_fail_count + 1)
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def lock_user(self, user_id: int) -> None:
        """
        锁定用户账号

        :param user_id: 用户 ID
        :return: None
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                status=UserStatusEnum.LOCKED,
                lock_time=datetime.now()
            )
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def reset_user_login_status(self, user_id: int) -> None:
        """
        重置用户登录相关状态：
        - 解锁账号（status = NORMAL）
        - 清空锁定时间 lock_time = None
        - 清空登录失败次数 login_fail_count = 0
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(
                status=UserStatusEnum.NORMAL,
                lock_time=None,
                login_fail_count=0
            )
        )
        await self.db_session.execute(stmt)
        await self.db_session.commit()
