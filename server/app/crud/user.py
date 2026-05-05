from datetime import datetime
from math import ceil
from sqlalchemy import delete, insert, select, update, func

from app.core.enums import UserStatusEnum
from app.crud.base import BaseCRUD
from app.models import User, Role, Post, UserRole, UserPost, PostRole
from app.schemas.user import UserListQueryRequest


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

    async def update_user_password(self, user_id: int, hashed_password: str) -> None:
        """
        更新用户密码

        :param user_id: 用户 ID
        :param hashed_password: 加密后的新密码
        :return: None
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(password=hashed_password)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def update_user_status(self, user_id: int, status: int) -> None:
        """
        更新用户状态

        :param user_id: 用户 ID
        :param status: 目标状态
        :return: None
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(status=status)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def update_user_info(self, user_id: int, user_data: dict) -> None:
        """
        更新用户基础信息

        :param user_id: 用户 ID
        :param user_data: 用户数据字典
        :return: None
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(**user_data)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def update_login_time(self, user_id: int) -> None:
        """
        更新用户登录时间

        :param user_id: 用户 ID
        :return: None
        """
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_date=datetime.now())
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def get_user_list(self, query: UserListQueryRequest) -> tuple[list[User], int, int, int]:
        """
        分页查询用户列表

        :param query: 查询条件
        :return: (用户列表, 总条数, 总页数, 当前页)
        """
        # 构建查询条件
        conditions = [User.del_flag == 0]
        
        if query.username:
            conditions.append(User.username.like(f"%{query.username}%"))
        if query.nickname:
            conditions.append(User.nickname.like(f"%{query.nickname}%"))
        if query.email:
            conditions.append(User.email.like(f"%{query.email}%"))
        if query.phone:
            conditions.append(User.phone.like(f"%{query.phone}%"))
        if query.status is not None:
            conditions.append(User.status == query.status)
        if query.dept_id:
            conditions.append(User.dept_id == query.dept_id)

        # 查询总条数
        count_stmt = select(func.count(User.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        # 计算总页数
        pages = ceil(total / query.page_size) if total > 0 else 1

        # 分页查询用户列表，按创建时间倒序
        offset = (query.page_num - 1) * query.page_size
        list_stmt = (
            select(User)
            .where(*conditions)
            .order_by(User.create_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        users = list(list_result.scalars().all())

        return users, total, pages, query.page_num

    async def get_user_role_ids(self, user_id: int) -> list[int]:
        """获取用户已绑定的角色ID列表

        Args:
            user_id: 用户ID

        Returns:
            list[int]: 角色ID列表
        """
        stmt = select(UserRole.role_id).where(UserRole.user_id == user_id)
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def add_roles_to_user(self, user_id: int, role_ids: list[int]) -> None:
        """批量新增用户角色关联

        Args:
            user_id: 用户ID
            role_ids: 要新增的角色ID列表
        """
        if not role_ids:
            return

        role_relations = [
            {"user_id": user_id, "role_id": role_id}
            for role_id in set(role_ids)
        ]
        
        insert_stmt = insert(UserRole).values(role_relations)
        await self.db_session.execute(insert_stmt)

    async def remove_roles_from_user(self, user_id: int, role_ids: list[int]) -> None:
        """批量删除用户角色关联

        Args:
            user_id: 用户ID
            role_ids: 要删除的角色ID列表
        """
        if not role_ids:
            return

        delete_stmt = (
            delete(UserRole)
            .where(
                UserRole.user_id == user_id,
                UserRole.role_id.in_(role_ids)
            )
        )
        await self.db_session.execute(delete_stmt)
