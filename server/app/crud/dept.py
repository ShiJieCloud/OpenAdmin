from sqlalchemy import select, func, update, delete

from app.crud.base import BaseCRUD
from app.models import Dept


class DeptCRUD(BaseCRUD):
    """部门 CRUD 操作类"""

    async def get_dept(self, dept_id: int) -> Dept | None:
        """根据部门ID获取部门详情

        Args:
            dept_id: 部门ID

        Returns:
            Dept | None: 部门对象或None
        """
        stmt = select(Dept).where(Dept.id == dept_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_dept_by_name(
        self,
        *,
        dept_name: str,
        parent_id: int,
        exclude_id: int | None = None
    ) -> Dept | None:
        """根据部门名称和父级ID获取部门详情

        Args:
            dept_name: 部门名称
            parent_id: 父级部门ID
            exclude_id: 排除的部门ID（用于编辑时校验）

        Returns:
            Dept | None: 部门对象或None
        """
        conditions = [
            Dept.dept_name == dept_name,
            Dept.parent_id == parent_id
        ]

        if exclude_id is not None:
            conditions.append(Dept.id != exclude_id)

        stmt = select(Dept).where(*conditions)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def count_children(self, parent_id: int) -> int:
        """统计子部门数量

        Args:
            parent_id: 父部门ID

        Returns:
            int: 子部门数量
        """
        stmt = select(func.count(Dept.id)).where(Dept.parent_id == parent_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one()

    async def create_dept(self, dept_data: dict) -> Dept:
        """创建部门

        Args:
            dept_data: 部门数据字典

        Returns:
            Dept: 创建后的部门对象
        """
        dept = Dept(**dept_data)
        self.db_session.add(dept)
        await self.db_session.flush()
        await self.db_session.refresh(dept)
        return dept

    async def update_dept(self, dept_id: int, dept_data: dict) -> None:
        """更新部门信息

        Args:
            dept_id: 部门ID
            dept_data: 更新数据字典
        """
        stmt = (
            update(Dept)
            .where(Dept.id == dept_id)
            .values(**dept_data)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def delete_dept(self, dept_id: int) -> None:
        """物理删除部门

        Args:
            dept_id: 部门ID
        """
        stmt = (
            delete(Dept)
            .where(Dept.id == dept_id)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def get_dept_list(self) -> list[Dept]:
        """获取部门列表

        Returns:
            list[Dept]: 部门列表（按sort升序）
        """

        stmt = (
            select(Dept)
            .order_by(Dept.sort.asc(), Dept.create_time.desc())
        )
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())
