from sqlalchemy import select, delete, update
from app.crud.base import BaseCRUD
from app.models import Menu, Permission, Role, RolePermission


class MenuCRUD(BaseCRUD):
    """菜单 CRUD 操作类"""

    async def create_menu(self, menu_data: dict) -> Menu:
        """创建菜单

        Args:
            menu_data: 菜单数据字典

        Returns:
            Menu: 创建后的菜单对象
        """
        menu = Menu(**menu_data)
        self.db_session.add(menu)
        await self.db_session.refresh(menu)
        return menu

    async def get_menu(self, menu_id: int) -> Menu | None:
        """根据菜单ID获取菜单

        Args:
            menu_id: 菜单ID

        Returns:
            Menu | None: 菜单对象或None
        """
        stmt = select(Menu).where(Menu.id == menu_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_children_count(self, parent_id: int) -> int:
        """获取子菜单数量

        Args:
            parent_id: 父菜单ID

        Returns:
            int: 子菜单数量
        """
        stmt = select(Menu).where(Menu.parent_id == parent_id)
        result = await self.db_session.execute(stmt)
        return len(result.scalars().all())

    async def update_menu(self, menu_id: int, menu_data: dict) -> None:
        """更新菜单

        Args:
            menu_id: 菜单ID
            menu_data: 更新数据字典

        Returns:
            None: 更新成功
        """

        stmt = (
            update(Menu)
            .where(Menu.id == menu_id)
            .values(**menu_data)
        )

        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def delete_menu(self, menu_id: int) -> None:
        """删除菜单

        Args:
            menu_id: 菜单ID

        Returns:
            None: 删除成功
        """
        stmt = delete(Menu).where(Menu.id == menu_id)
        await self.db_session.execute(stmt)
        await self.db_session.commit()

    async def get_menus(self) -> list[Menu]:
        """获取所有菜单列表（按 sort 排序）

        Returns:
            list[Menu]: 菜单列表
        """
        stmt = select(Menu).where(Menu.status == 0).order_by(Menu.sort.asc())
        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_menus_by_role_codes(self, role_codes: list[str]) -> list[Menu]:
        """根据角色编码获取关联的菜单列表（去重）

        Args:
            role_codes: 角色编码列表

        Returns:
            list[Menu]: 菜单列表
        """
        if not role_codes:
            return []

        stmt = (
            select(Menu)
            .distinct()
            .join(Permission, Permission.menu_id == Menu.id)
            .join(RolePermission, RolePermission.perm_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .where(
                Role.role_code.in_(role_codes),
                Role.status == 0,
                Menu.is_hidden == 0,
                Menu.status == 0,
            )
            .order_by(Menu.sort.asc())
        )

        result = await self.db_session.execute(stmt)
        return result.scalars().all()

    async def get_menus_with_parents(self, menu_ids: list[int]) -> list[Menu]:
        """递归获取菜单及其所有父菜单（使用WITH RECURSIVE）

        Args:
            menu_ids: 菜单ID列表

        Returns:
            list[Menu]: 菜单及其父菜单列表
        """
        if not menu_ids:
            return []

        sql = """
            WITH RECURSIVE menu_tree AS (
                SELECT * FROM sys_menu WHERE id IN :menu_ids
                UNION ALL
                SELECT m.* FROM sys_menu m
                JOIN menu_tree mt ON mt.parent_id = m.id
            )
            SELECT * FROM menu_tree WHERE status = 0 AND ORDER BY parent_id, sort;
        """

        result = await self.db_session.execute(sql, {"menu_ids": tuple(menu_ids)})
        return result.scalars().all()
