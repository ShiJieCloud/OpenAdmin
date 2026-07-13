from app.core.enums import PermTypeEnum
from sqlalchemy import select

from app.crud.base import BaseCRUD
from app.models import Permission, Role, RolePermission


class PermissionCRUD(BaseCRUD):
    """权限 CRUD 操作类"""

    async def get_all_permissions(self) -> list[Permission]:
        """获取所有权限列表（按 sort 升序）"""
        stmt = select(Permission).order_by(Permission.sort.asc())
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_perms_by_role_codes(
        self,
        role_codes: list[str],
        perm_type: PermTypeEnum | None = None
    ) -> list[Permission]:
        """根据角色编码列表查询权限列表

        三表联查：sys_role → sys_role_permission → sys_permission

        Args:
            role_codes: 角色编码列表
            perm_type: 权限类型（可选）
        """
        if not role_codes:
            return []

        conditions = [Role.role_code.in_(role_codes)]
        if perm_type is not None:
            conditions.append(Permission.type == perm_type)

        stmt = (
            select(Permission)
            .distinct()
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(*conditions)
        )

        result = await self.db_session.execute(stmt)
        return result.scalars().all()
