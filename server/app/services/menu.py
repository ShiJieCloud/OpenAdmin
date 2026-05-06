from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud.menu import MenuCRUD
from app.models import Menu
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest
from app.services.base import BaseService


class MenuService(BaseService):
    """菜单服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.menu_crud = MenuCRUD(db_session)

    async def create_menu(self, req: MenuCreateRequest) -> Menu:
        """创建菜单

        Args:
            req: 创建菜单请求

        Returns:
            Menu: 创建后的菜单对象

        Raises:
            BusinessError: 父菜单不存在
        """
        if req.parent_id != 0:
            parent_menu = await self.menu_crud.get_menu(req.parent_id)
            if not parent_menu:
                raise BusinessError(RespCodeEnum.MENU_PARENT_NOT_EXIST)

        menu_data = req.model_dump()
        return await self.menu_crud.create_menu(menu_data)

    async def get_menu(self, menu_id: int) -> Menu:
        """获取菜单详情

        Args:
            menu_id: 菜单ID

        Returns:
            Menu: 菜单对象

        Raises:
            BusinessError: 菜单不存在
        """
        menu = await self.menu_crud.get_menu(menu_id)
        if not menu:
            raise BusinessError(RespCodeEnum.MENU_NOT_EXIST)
        return menu

    async def update_menu(self, menu_id: int, req: MenuUpdateRequest) -> None:
        """更新菜单

        Args:
            menu_id: 菜单ID
            req: 更新菜单请求

        Raises:
            BusinessError: 菜单不存在或父菜单设置无效
        """
        menu = await self.menu_crud.get_menu(menu_id)
        if not menu:
            raise BusinessError(RespCodeEnum.MENU_NOT_EXIST)

        if req.parent_id is not None:
            if req.parent_id == menu_id:
                raise BusinessError(RespCodeEnum.MENU_PARENT_CANNOT_BE_SELF)

            if req.parent_id != 0:
                parent_menu = await self.menu_crud.get_menu(req.parent_id)
                if not parent_menu:
                    raise BusinessError(RespCodeEnum.MENU_PARENT_NOT_EXIST)

        update_data = req.model_dump(exclude_unset=True)
        await self.menu_crud.update_menu(menu_id, update_data)

    async def delete_menu(self, menu_id: int) -> None:
        """删除菜单

        Args:
            menu_id: 菜单ID
            recursive: 是否递归删除子菜单

        Raises:
            BusinessError: 菜单不存在或存在子菜单
        """
        menu = await self.menu_crud.get_menu(menu_id)
        if not menu:
            raise BusinessError(RespCodeEnum.MENU_NOT_EXIST)

        children_count = await self.menu_crud.get_children_count(menu_id)

        if children_count > 0:
            raise BusinessError(RespCodeEnum.MENU_HAS_CHILDREN)
        
        await self.menu_crud.delete_menu(menu_id)
