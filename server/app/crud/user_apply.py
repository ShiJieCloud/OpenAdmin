from datetime import datetime
from math import ceil
from sqlalchemy import select, update, func

from app.crud.base import BaseCRUD
from app.models import UserApply
from app.schemas.user_apply import UserApplyListQueryRequest


class UserApplyCRUD(BaseCRUD):
    """用户注册申请 CRUD 操作类"""

    async def get_apply(self, apply_id: int) -> UserApply | None:
        """根据ID获取申请（排除软删除）

        Args:
            apply_id: 申请ID

        Returns:
            申请对象或 None
        """
        stmt = select(UserApply).where(
            UserApply.id == apply_id,
            UserApply.del_flag == 0
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_pending_apply(self, username: str) -> UserApply | None:
        """根据用户名查询待审核申请（status=0）

        Args:
            username: 登录账号

        Returns:
            待审核申请对象或 None
        """
        stmt = select(UserApply).where(
            UserApply.username == username,
            UserApply.status == 0,
            UserApply.del_flag == 0
        )
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_apply(self, apply_data: dict) -> UserApply:
        """创建用户注册申请

        Args:
            apply_data: 申请数据字典

        Returns:
            创建后的申请对象
        """
        apply = UserApply(**apply_data)
        self.db_session.add(apply)
        await self.db_session.flush()
        await self.db_session.refresh(apply)
        return apply

    async def get_apply_list(self, query: UserApplyListQueryRequest) -> tuple[list[UserApply], int, int, int]:
        """分页查询申请列表

        Args:
            query: 查询条件

        Returns:
            (申请列表, 总条数, 总页数, 当前页码)
        """
        conditions = [UserApply.del_flag == 0]

        if query.username:
            conditions.append(UserApply.username.like(f"%{query.username}%"))
        if query.phone:
            conditions.append(UserApply.phone.like(f"%{query.phone}%"))
        if query.status is not None:
            conditions.append(UserApply.status == query.status)

        # 查询总条数
        count_stmt = select(func.count(UserApply.id)).where(*conditions)
        count_result = await self.db_session.execute(count_stmt)
        total = count_result.scalar_one()

        # 计算总页数
        pages = ceil(total / query.page_size) if total > 0 else 1

        # 分页查询列表，按创建时间倒序
        offset = (query.page_num - 1) * query.page_size
        list_stmt = (
            select(UserApply)
            .where(*conditions)
            .order_by(UserApply.create_time.desc())
            .offset(offset)
            .limit(query.page_size)
        )
        list_result = await self.db_session.execute(list_stmt)
        records = list(list_result.scalars().all())

        return records, total, pages, query.page_num

    async def update_audit_status(
        self,
        apply_id: int,
        status: int,
        audit_user_id: int,
        audit_time: datetime,
        audit_reason: str | None = None
    ) -> None:
        """更新申请审批状态

        Args:
            apply_id: 申请ID
            status: 目标状态：1=已通过 2=已拒绝
            audit_user_id: 审批管理员ID
            audit_time: 审批时间
            audit_reason: 审批意见/拒绝原因（可选）
        """
        values = {
            "status": status,
            "audit_user_id": audit_user_id,
            "audit_time": audit_time,
        }
        if audit_reason is not None:
            values["audit_reason"] = audit_reason

        stmt = (
            update(UserApply)
            .where(UserApply.id == apply_id)
            .values(**values)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()
