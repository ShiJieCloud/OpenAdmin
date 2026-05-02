from app.core.enums import PermTypeEnum
from app.crud import PermissionCRUD
from app.models import Permission
from app.services.base import BaseService


class PermissionService(BaseService):
    """权限服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.permission_crud = PermissionCRUD(db_session)

    async def get_perms_by_role_codes(
        self,
        role_codes: list[str],
        perm_type: PermTypeEnum | None = None
    ) -> list[Permission]:
        """根据角色编码列表查询权限列表

        Args:
            role_codes: 角色编码列表
            perm_type: 权限类型（可选）

        Returns:
            list[Permission]: 权限列表
        """
        return await self.permission_crud.get_perms_by_role_codes(role_codes, perm_type)
