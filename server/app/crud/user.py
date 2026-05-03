from datetime import datetime
from sqlalchemy import select, update

from app.core.enums import UserStatusEnum
from app.crud.base import BaseCRUD
from app.models import User, Role, Post, UserRole, UserPost, PostRole


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

    async def get_user_roles(self, user_id: int) -> list[Role]:
        """
        获取用户所有角色（直接角色 + 岗位间接角色）

        SQL 对应逻辑：
            SELECT DISTINCT sr.*
            FROM sys_role sr
            LEFT JOIN sys_post_role spr ON sr.id = spr.role_id
            LEFT JOIN sys_post sp ON spr.post_id = sp.id
            LEFT JOIN sys_user_post sup ON sp.id = sup.post_id
            LEFT JOIN sys_user_role sur ON sr.id = sur.role_id
            WHERE sup.user_id = :user_id 
               OR sur.user_id = :user_id
        """
        stmt = (
            select(Role)
            .distinct()
            # 岗位 → 角色 关联
            .outerjoin(PostRole, PostRole.role_id == Role.id)
            # 岗位表
            .outerjoin(Post, Post.id == PostRole.post_id)
            # 用户 → 岗位 关联
            .outerjoin(UserPost, (UserPost.post_id == Post.id) & (UserPost.user_id == user_id))
            # 用户 → 角色 直接关联
            .outerjoin(UserRole, (UserRole.role_id == Role.id) & (UserRole.user_id == user_id))
            # 岗位链路 或 直接分配，任一满足即可
            .where(
                (UserPost.user_id == user_id) | (UserRole.user_id == user_id)
            )
        )

        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def create_user(self, user_data: dict) -> User:
        """
        创建新用户

        :param user_data: 用户数据字典
        :return: 创建后的用户对象
        """
        
        user = User(**user_data)
        self.db_session.add(user)
        await self.db_session.flush()
        await self.db_session.refresh(user)
        return user
