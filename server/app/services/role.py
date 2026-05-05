from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import RoleCRUD
from app.models import Role
from app.schemas.role import RoleCreateRequest, RoleUpdateRequest, RoleUpdateStatusRequest, RoleListQueryRequest
from app.services.base import BaseService


class RoleService(BaseService):
    """角色服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.role_crud = RoleCRUD(db_session)

    async def get_role(self, role_id: int) -> Role:
        """获取角色详情

        Args:
            role_id: 角色ID

        Returns:
            Role: 角色对象

        Raises:
            BusinessError: 角色不存在
        """
        role = await self.role_crud.get_role(role_id)
        if not role:
            raise BusinessError(RespCodeEnum.ROLE_NOT_EXIST)
        return role

    async def create_role(self, req: RoleCreateRequest) -> Role:
        """创建角色

        Args:
            req: 创建角色请求

        Returns:
            Role: 创建后的角色对象

        Raises:
            BusinessError: 角色编码已存在 / 角色名称已存在
        """
        existing_role = await self.role_crud.get_role_by_key(role_code=req.role_code)
        if existing_role:
            raise BusinessError(RespCodeEnum.ROLE_CODE_EXIST)

        existing_role = await self.role_crud.get_role_by_key(role_name=req.role_name)
        if existing_role:
            raise BusinessError(RespCodeEnum.ROLE_NAME_EXIST)

        role_data = req.model_dump()
        return await self.role_crud.create_role(role_data)

    async def update_role(self, req: RoleUpdateRequest) -> Role:
        """更新角色信息

        Args:
            req: 更新角色请求

        Returns:
            Role: 更新后的角色对象

        Raises:
            BusinessError: 角色不存在 / 角色编码已存在 / 角色名称已存在
        """

        # 校验角色是否存在
        role = await self.role_crud.get_role(req.role_id)
        if not role:
            raise BusinessError(RespCodeEnum.ROLE_NOT_EXIST)

        # 校验角色编码是否存在
        if req.role_code and req.role_code != role.role_code:
            existing_role = await self.role_crud.get_role_by_key(role_code=req.role_code)
            if existing_role:
                raise BusinessError(RespCodeEnum.ROLE_CODE_EXIST)

        # 校验角色名称是否存在
        if req.role_name and req.role_name != role.role_name:
            existing_role = await self.role_crud.get_role_by_key(role_name=req.role_name, exclude_id=req.role_id)
            if existing_role:
                raise BusinessError(RespCodeEnum.ROLE_NAME_EXIST)

        # 构造更新数据：仅包含已赋值的字段（排除主键 role_id 不参与更新）
        update_data = req.model_dump(exclude_unset=True, exclude={"role_id"})
        if update_data:
            await self.role_crud.update_role(req.role_id, update_data)
            role = await self.role_crud.get_role(req.role_id)

        return role

    async def delete_role(self, role_id: int) -> None:
        """删除角色（物理删除）

        Args:
            role_id: 角色ID

        Raises:
            BusinessError: 角色不存在 / 角色已分配给用户 / 角色已分配给岗位
        """
        role = await self.role_crud.get_role(role_id)
        if not role:
            raise BusinessError(RespCodeEnum.ROLE_NOT_EXIST)

        user_count = await self.role_crud.count_users_by_role(role_id)
        if user_count > 0:
            raise BusinessError(RespCodeEnum.ROLE_HAS_USER)

        post_count = await self.role_crud.count_posts_by_role(role_id)
        if post_count > 0:
            raise BusinessError(RespCodeEnum.ROLE_HAS_POST)

        await self.role_crud.delete_role(role_id)

    async def update_role_status(self, req: RoleUpdateStatusRequest) -> Role:
        """更新角色状态

        Args:
            req: 更新角色状态请求

        Returns:
            Role: 更新后的角色对象

        Raises:
            BusinessError: 角色不存在
        """
        role = await self.role_crud.get_role(req.role_id)
        if not role:
            raise BusinessError(RespCodeEnum.ROLE_NOT_EXIST)

        await self.role_crud.update_role(req.role_id, {"status": req.status})
        role = await self.role_crud.get_role(req.role_id)
        return role

    async def get_role_list(self, query: RoleListQueryRequest) -> tuple[list[Role], int, int, int]:
        """分页查询角色列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Role], int, int, int]: (角色列表, 总条数, 总页数, 当前页)
        """
        return await self.role_crud.get_role_list(query)
