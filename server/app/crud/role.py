from math import ceil
from sqlalchemy import select, func, update, delete

from app.crud.base import BaseCRUD
from app.models import Role, UserRole, PostRole, RolePermission
from app.schemas.role import RoleListQueryRequest


class RoleCRUD(BaseCRUD):
    """角色 CRUD 操作类"""

    async def get_role(self, role_id: int) -> Role | None:
        """根据角色ID获取角色详情

        Args:
            role_id: 角色ID

        Returns:
            Role | None: 角色对象或None
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_by_key(
        self,
        *,
        role_code: str | None = None,
        role_name: str | None = None,
        exclude_id: int | None = None
    ) -> Role | None:
        """根据角色编码或角色名称获取角色详情

        Args:
            role_code: 角色编码（可选）
            role_name: 角色名称（可选）
            exclude_id: 排除的角色ID（用于编辑时校验）

        Returns:
            Role | None: 角色对象或None
        """
        conditions = []

        if role_code is not None:
            conditions.append(Role.role_code == role_code)
        if role_name is not None:
            conditions.append(Role.role_name == role_name)
        if exclude_id is not None:
            conditions.append(Role.id != exclude_id)

        if not conditions:
            return None

        stmt = select(Role).where(*conditions)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_roles(self) -> int:
        """统计角色总数

        Returns:
            int: 角色数量
        """
        stmt = select(func.count(Role.id))
        result = await self.db_session.execute(stmt)
        return result.scalar_one()

    async def count_users_by_role(self, role_id: int) -> int:
        """统计角色关联的用户数量

        Args:
            role_id: 角色ID

        Returns:
            int: 用户数量
        """
        stmt = select(func.count(UserRole.id)).where(UserRole.role_id == role_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one()

    async def count_posts_by_role(self, role_id: int) -> int:
        """统计角色关联的岗位数量

        Args:
            role_id: 角色ID

        Returns:
            int: 岗位数量
        """
        stmt = select(func.count(PostRole.id)).where(PostRole.role_id == role_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one()

    async def create_role(self, role_data: dict) -> Role:
        """创建角色

        Args:
            role_data: 角色数据字典

        Returns:
            Role: 创建后的角色对象
        """
        role = Role(**role_data)
        self.db_session.add(role)
        await self.db_session.flush()
        await self.db_session.refresh(role)
        return role

    async def update_role(self, role_id: int, role_data: dict) -> None:
        """更新角色信息

        Args:
            role_id: 角色ID
            role_data: 更新数据字典
        """
        stmt = (
            update(Role)
            .where(Role.id == role_id)
            .values(**role_data)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def delete_role(self, role_id: int) -> None:
        """物理删除角色

        Args:
            role_id: 角色ID
        """
        stmt = (
            delete(Role)
            .where(Role.id == role_id)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def get_role_list(self, query: RoleListQueryRequest) -> tuple[list[Role], int, int, int]:
        """分页查询角色列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Role], int, int, int]: (角色列表, 总条数, 总页数, 当前页)
        """
        conditions = []

        if query.role_name:
            conditions.append(Role.role_name.like(f"%{query.role_name}%"))
        if query.role_code:
            conditions.append(Role.role_code.like(f"%{query.role_code}%"))
        if query.status is not None:
            conditions.append(Role.status == query.status)

        count_stmt = select(func.count(Role.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        pages = ceil(total / query.page_size) if total > 0 else 1

        offset = (query.page_num - 1) * query.page_size
        list_stmt = (
            select(Role)
            .where(*conditions)
            .order_by(Role.sort.asc(), Role.create_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        roles = list_result.scalars().all()

        return roles, total, pages, query.page_num

    async def assign_permissions(self, role_id: int, perm_ids: list[int]) -> None:
        """分配角色权限

        全量覆盖指定角色的权限列表。

        Args:
            role_id: 角色ID
            perm_ids: 权限ID列表
        """
        stmt = delete(RolePermission).where(RolePermission.role_id == role_id)
        await self.db_session.execute(stmt)

        if perm_ids:
            objs = [RolePermission(role_id=role_id, perm_id=pid) for pid in perm_ids]
            self.db_session.add_all(objs)

        await self.db_session.flush()

    async def get_role_permissions(self, role_id: int) -> list:
        """获取角色关联的权限列表

        Args:
            role_id: 角色ID

        Returns:
            list[Permission]: 权限对象列表
        """
        from app.models import Permission
        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .where(RolePermission.role_id == role_id)
            .order_by(Permission.sort.asc())
        )
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())
