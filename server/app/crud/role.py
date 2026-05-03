from math import ceil
from sqlalchemy import select, func

from app.crud.base import BaseCRUD
from app.models import Role
from app.schemas.role import RoleListQueryRequest


class RoleCRUD(BaseCRUD):
    """角色 CRUD 操作类"""

    async def get_role(self, role_id: int) -> Role | None:
        """根据角色ID获取角色详情

        Args:
            role_id: 角色ID

        Returns:
            Role | None: 角色对象或None
        """
        stmt = select(Role).where(Role.id == role_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_role_list(self, query: RoleListQueryRequest) -> tuple[list[Role], int, int, int]:
        """分页查询角色列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Role], int, int, int]: (角色列表, 总条数, 总页数, 当前页)
        """
        conditions = []

        if query.role_name:
            conditions.append(Role.role_name.like(f"%{query.role_name}%"))
        if query.role_code:
            conditions.append(Role.role_code.like(f"%{query.role_code}%"))
        if query.status is not None:
            conditions.append(Role.status == query.status)

        count_stmt = select(func.count(Role.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        pages = ceil(total / query.page_size) if total > 0 else 1

        offset = (query.page_num - 1) * query.page_size
        list_stmt = (
            select(Role)
            .where(*conditions)
            .order_by(Role.sort.asc(), Role.create_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        roles = list_result.scalars().all()

        return roles, total, pages, query.page_num
