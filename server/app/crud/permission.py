from math import ceil
from sqlalchemy import select, func, update, delete
from app.crud.base import BaseCRUD
from app.models import Permission, Role, RolePermission
from app.schemas.permission import PermissionListQueryRequest


class PermissionCRUD(BaseCRUD):
    """权限 CRUD 操作类"""

    async def get_all_permissions(self) -> list[Permission]:
        """获取所有权限列表（按 sort 升序）"""
        stmt = select(Permission).order_by(Permission.sort.asc())
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_permission(self, perm_id: int) -> Permission | None:
        """根据权限ID获取权限详情

        Args:
            perm_id: 权限ID

        Returns:
            Permission | None: 权限对象或None
        """
        stmt = select(Permission).where(Permission.id == perm_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_permission_by_code(self, code: str, exclude_id: int | None = None) -> Permission | None:
        """根据权限编码获取权限

        Args:
            code: 权限编码
            exclude_id: 排除的权限ID（用于编辑时校验）

        Returns:
            Permission | None: 权限对象或None
        """
        conditions = [Permission.code == code]
        if exclude_id is not None:
            conditions.append(Permission.id != exclude_id)

        stmt = select(Permission).where(*conditions)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_permission(self, perm_data: dict) -> Permission:
        """创建权限

        Args:
            perm_data: 权限数据字典

        Returns:
            Permission: 创建后的权限对象
        """
        perm = Permission(**perm_data)
        self.db_session.add(perm)
        await self.db_session.flush()
        await self.db_session.refresh(perm)
        return perm

    async def update_permission(self, perm_id: int, perm_data: dict) -> None:
        """更新权限信息

        Args:
            perm_id: 权限ID
            perm_data: 更新数据字典
        """
        stmt = (
            update(Permission)
            .where(Permission.id == perm_id)
            .values(**perm_data)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def delete_permission(self, perm_id: int) -> None:
        """物理删除权限

        Args:
            perm_id: 权限ID
        """
        # 先删除角色权限关联表中的数据
        stmt = delete(RolePermission).where(RolePermission.perm_id == perm_id)
        await self.db_session.execute(stmt)

        # 再删除权限本身
        stmt = delete(Permission).where(Permission.id == perm_id)
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def list_permissions(self, query: PermissionListQueryRequest) -> tuple[list[Permission], int, int, int]:
        """分页查询权限列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Permission], int, int, int]: (权限列表, 总条数, 总页数, 当前页)
        """
        conditions = []

        if query.name:
            conditions.append(Permission.name.like(f"%{query.name}%"))
        if query.code:
            conditions.append(Permission.code.like(f"%{query.code}%"))
        if query.status is not None:
            conditions.append(Permission.status == query.status)
        if query.menu_id is not None:
            conditions.append(Permission.menu_id == query.menu_id)

        count_stmt = select(func.count(Permission.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        pages = ceil(total / query.page_size) if total > 0 else 1

        offset = (query.page_num - 1) * query.page_size
        list_stmt = (
            select(Permission)
            .where(*conditions)
            .order_by(Permission.sort.asc(), Permission.create_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        perms = list_result.scalars().all()

        return perms, total, pages, query.page_num

    async def get_perms_by_role_codes(
        self,
        role_codes: list[str],
        perm_status: int | None = None,
    ) -> list[Permission]:
        """根据角色编码列表查询权限列表

        三表联查：sys_role → sys_role_permission → sys_permission

        Args:
            role_codes: 角色编码列表
            perm_status: 权限状态（可选）
        """
        if not role_codes:
            return []

        conditions = [Role.role_code.in_(role_codes)]

        # 过滤权限状态
        if perm_status is not None:
            conditions.append(Permission.status == perm_status)

        stmt = (
            select(Permission)
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(*conditions)
        )

        result = await self.db_session.execute(stmt)
        return result.scalars().all()
