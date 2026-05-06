from sqlalchemy import select, delete, update
from app.crud.base import BaseCRUD
from app.models import Menu


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
        await self.db_session.commit()
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
