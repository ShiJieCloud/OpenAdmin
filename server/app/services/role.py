from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud import RoleCRUD
from app.models import Role
from app.schemas.role import RoleListQueryRequest
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
            raise BusinessError(RespCodeEnum.NOT_FOUND, msg="角色不存在")
        return role

    async def get_role_list(self, query: RoleListQueryRequest) -> tuple[list[Role], int, int, int]:
        """分页查询角色列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Role], int, int, int]: (角色列表, 总条数, 总页数, 当前页)
        """
        return await self.role_crud.get_role_list(query)
