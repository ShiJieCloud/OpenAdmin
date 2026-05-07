from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud.menu import MenuCRUD
from app.models import Menu
from app.schemas.menu import MenuCreateRequest, MenuUpdateRequest, MenuTreeResponse
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

    async def get_menu_list(self) -> list[Menu]:
        """获取所有菜单列表

        Returns:
            list[Menu]: 菜单列表
        """
        return await self.menu_crud.get_menus()

    async def get_user_menu_tree(self, role_codes: list[str], is_superuser: bool = False) -> list[MenuTreeResponse]:
        """获取当前用户的权限菜单树（前端侧边栏使用）
        - 超级管理员：返回全部菜单
        - 普通用户：返回有权限的菜单 + 自动包含所有父级目录
        """
        # 1. 超级管理员直接获取所有菜单
        if is_superuser:
            menus = await self.menu_crud.get_menus()
    
        # 2. 普通用户按角色权限获取菜单
        else:
            # 无角色 → 直接返回空
            if not role_codes:
                return []
        
            # 获取角色有权限的页面
            user_menus = await self.menu_crud.get_menus_by_role_codes(role_codes)
            if not user_menus:
                return []

            # 批量获取页面 + 所有祖先目录
            menu_ids = [m.id for m in user_menus]
            menus = await self.menu_crud.get_menus_with_parents(menu_ids)

        # 3. 无任何菜单 → 返回空
        if not menus:
            return []

        # 4. 构建树形结构
        return self._build_menu_tree(menus, parent_id=0)

    def _build_menu_tree(self, menus: list[Menu], parent_id: int = 0) -> List[MenuTreeResponse]:
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
