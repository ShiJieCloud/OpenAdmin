from app.core.enums import RespCodeEnum, PermStatusEnum
from app.core.exceptions import BusinessError
from app.crud import PermissionCRUD
from app.models import Permission
from app.schemas.permission import PermissionCreateRequest, PermissionUpdateRequest, PermissionListQueryRequest
from app.services.base import BaseService


class PermissionService(BaseService):
    """权限服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.permission_crud = PermissionCRUD(db_session)

    async def get_all_permissions(self) -> list[Permission]:
        """获取所有权限列表"""
        return await self.permission_crud.get_all_permissions()

    async def get_permission(self, perm_id: int) -> Permission:
        """获取权限详情

        Args:
            perm_id: 权限ID

        Returns:
            Permission: 权限对象

        Raises:
            BusinessError: 权限不存在
        """
        perm = await self.permission_crud.get_permission(perm_id)
        if not perm:
            raise BusinessError(RespCodeEnum.PERM_NOT_EXIST)
        return perm

    async def create_permission(self, req: PermissionCreateRequest) -> Permission:
        """创建权限

        Args:
            req: 创建权限请求

        Returns:
            Permission: 创建后的权限对象

        Raises:
            BusinessError: 权限编码已存在
        """
        existing_perm = await self.permission_crud.get_permission_by_code(code=req.code)
        if existing_perm:
            raise BusinessError(RespCodeEnum.PERM_CODE_EXIST)

        perm_data = req.model_dump()
        return await self.permission_crud.create_permission(perm_data)

    async def update_permission(self, req: PermissionUpdateRequest) -> Permission:
        """更新权限信息

        Args:
            req: 更新权限请求

        Returns:
            Permission: 更新后的权限对象

        Raises:
            BusinessError: 权限不存在 / 权限编码已存在
        """
        # 校验权限是否存在
        perm = await self.permission_crud.get_permission(req.perm_id)
        if not perm:
            raise BusinessError(RespCodeEnum.PERM_NOT_EXIST)

        # 校验权限编码是否存在
        if req.code and req.code != perm.code:
            existing_perm = await self.permission_crud.get_permission_by_code(code=req.code, exclude_id=req.perm_id)
            if existing_perm:
                raise BusinessError(RespCodeEnum.PERM_CODE_EXIST)

        # 构造更新数据
        update_data = req.model_dump(exclude_unset=True, exclude={"perm_id"})
        if update_data:
            await self.permission_crud.update_permission(req.perm_id, update_data)
            perm = await self.permission_crud.get_permission(req.perm_id)

        return perm

    async def delete_permission(self, perm_id: int) -> None:
        """删除权限

        Args:
            perm_id: 权限ID

        Raises:
            BusinessError: 权限不存在
        """
        perm = await self.permission_crud.get_permission(perm_id)
        if not perm:
            raise BusinessError(RespCodeEnum.PERM_NOT_EXIST)

        await self.permission_crud.delete_permission(perm_id)

    async def get_permission_list(self, query: PermissionListQueryRequest) -> tuple[list[Permission], int, int, int]:
        """分页查询权限列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Permission], int, int, int]: (权限列表, 总条数, 总页数, 当前页)
        """
        return await self.permission_crud.list_permissions(query)

    async def get_perms_by_role_codes(
        self,
        role_codes: list[str],
        perm_status: PermStatusEnum | None = None,
    ) -> list[Permission]:
        """根据角色编码列表查询权限列表

        Args:
            role_codes: 角色编码列表
            perm_status: 权限状态（可选）

        Returns:
            list[Permission]: 权限列表
        """
        return await self.permission_crud.get_perms_by_role_codes(role_codes, perm_status.value if perm_status else None)
