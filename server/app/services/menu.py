from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud.menu import MenuCRUD
from app.models import Menu
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest, MenuUpdateStatusRequest, MenuTreeResponse
from app.services.base import BaseService
from typing import List


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

    async def update_menu_status(self, req: MenuUpdateStatusRequest) -> None:
        """更新菜单状态（启用/禁用）

        Args:
            req: 更新状态请求

        Raises:
            BusinessError: 菜单不存在或状态值无效
        """
        if req.status not in (0, 1):
            raise BusinessError(RespCodeEnum.MENU_STATUS_INVALID)

        menu = await self.menu_crud.get_menu(req.menu_id)
        if not menu:
            raise BusinessError(RespCodeEnum.MENU_NOT_EXIST)

        await self.menu_crud.update_menu(req.menu_id, {"status": req.status})

    async def delete_menu(self, menu_id: int) -> None:
        """删除菜单

        Args:
            menu_id: 菜单ID

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

    async def get_menu_list(self) -> list[Menu]:
        """获取所有菜单列表

        Returns:
            list[Menu]: 菜单列表
        """
        return await self.menu_crud.get_menus()

    async def get_user_menu_tree(self, role_codes: list[str], is_superuser: bool = False) -> List[MenuTreeResponse]:
        """获取当前用户的权限菜单树（用于前端侧边栏）

        Args:
            role_codes: 用户的角色编码列表
            is_superuser: 是否超级管理员

        Returns:
            List[MenuTreeResponse]: 用户的权限菜单树
        """
        if is_superuser:
            menus = await self.menu_crud.get_menus()
        else:
            user_menus = await self.menu_crud.get_menus_by_role_codes(role_codes)
            if not user_menus:
                return []
            
            menu_ids = [m.id for m in user_menus]
            menus = await self.menu_crud.get_menus_with_parents(menu_ids)

        return self._build_menu_tree(menus, 0)

    def _build_menu_tree(self, menus: list[Menu], parent_id: int) -> List[MenuTreeResponse]:
        """递归构建菜单树

        Args:
            menus: 所有菜单列表
            parent_id: 父菜单ID

        Returns:
            List[MenuTreeResponse]: 菜单树
        """
        tree = []
        for menu in menus:
            if menu.parent_id == parent_id:
                children = self._build_menu_tree(menus, menu.id)
                menu_tree = MenuTreeResponse(
                    id=menu.id,
                    menu_name=menu.menu_name,
                    parent_id=menu.parent_id,
                    sort=menu.sort,
                    path=menu.path,
                    component=menu.component,
                    menu_type=menu.menu_type,
                    icon=menu.icon,
                    is_hidden=menu.is_hidden,
                    is_frame=menu.is_frame,
                    children=children
                )
                tree.append(menu_tree)
        return tree
