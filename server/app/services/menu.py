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

    async def batch_delete_menus(self, menu_ids: list[int]) -> None:
        """批量删除菜单

        逻辑：
        - 如果菜单存在子菜单，但子菜单也在删除列表中，允许删除
        - 如果菜单存在子菜单，但子菜单不在删除列表中，不允许删除

        Args:
            menu_ids: 菜单ID列表

        Raises:
            BusinessError: 存在子菜单不在删除列表中的菜单项
        """
        if not menu_ids:
            return

        menu_id_set = set(menu_ids)

        # 一次性查询所有待删除菜单的子菜单ID
        all_children = await self.menu_crud.get_descendants_by_parent_ids(menu_ids)
        all_children_ids = set([child.id for child in all_children])

        # 检查是否有子菜单不在删除列表中（即会成为孤儿菜单）
        orphan_children = all_children_ids - menu_id_set
        if orphan_children:
            first_orphan_id = next(iter(orphan_children))
            orphan_menu = await self.menu_crud.get_menu(first_orphan_id)
            label = orphan_menu.label if orphan_menu else str(first_orphan_id)
            raise BusinessError(
                RespCodeEnum.MENU_BATCH_HAS_CHILDREN,
                label=label,
            )

        await self.menu_crud.batch_delete_menus(menu_ids)

    async def get_menu_list(self) -> list[Menu]:
        """获取所有菜单列表

        Returns:
            list[Menu]: 菜单列表
        """
        return await self.menu_crud.get_menus()

    async def get_user_menu_list(self, role_codes: list[str], is_superuser: bool = False) -> list[Menu]:
        """获取当前用户的权限菜单列表（扁平结构）

        Args:
            role_codes: 用户的角色编码列表
            is_superuser: 是否超级管理员

        Returns:
            list[Menu]: 用户的权限菜单列表
        """
        if is_superuser:
            return await self.menu_crud.get_menus()

        user_menus = await self.menu_crud.get_menus_by_role_codes(role_codes)
        if not user_menus:
            return []

        menu_ids = [m.id for m in user_menus]
        return await self.menu_crud.get_menus_with_parents(menu_ids)

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
                menu_tree = MenuTreeResponse.model_validate(menu)
                menu_tree.children = children
                tree.append(menu_tree)
        return tree
