from sqlalchemy import select

from app.crud.base import BaseCRUD
from app.models import Post, Role, PostRole


class PostCRUD(BaseCRUD):
    """岗位 CRUD 操作类"""

    async def get_post(self, post_id: int) -> Post | None:
        """根据岗位ID获取岗位详情

        Args:
            post_id: 岗位ID

        Returns:
            Post | None: 岗位对象或None
        """
        stmt = select(Post).where(Post.id == post_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_posts_roles(self, post_ids: list[int]) -> list[Role]:
        """
        批量获取多个岗位关联的角色列表（去重）

        Args:
            post_ids: 岗位ID列表

        Returns:
            list[Role]: 去重后的角色列表
        """
        if not post_ids:
            return []

        stmt = (
            select(Role)
            .distinct()
            .join(PostRole, PostRole.role_id == Role.id)
            .where(
                PostRole.post_id.in_(post_ids),
                Role.status == 0
            )
        )

        result = await self.db_session.execute(stmt)
        return result.scalars().all()