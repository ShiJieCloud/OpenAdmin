from sqlalchemy import select, func, update, delete, insert

from app.crud.base import BaseCRUD
from app.models import Post, Role, PostRole
from app.schemas.post import PostListQueryRequest


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

    async def get_post_by_name(self, post_name: str, exclude_id: int | None = None) -> Post | None:
        """根据岗位名称获取岗位

        Args:
            post_name: 岗位名称
            exclude_id: 排除的岗位ID（用于编辑时校验）

        Returns:
            Post | None: 岗位对象或None
        """
        stmt = select(Post).where(Post.post_name == post_name)
        if exclude_id:
            stmt = stmt.where(Post.id != exclude_id)
        result = await self.db_session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_posts(
        self,
        query: PostListQueryRequest
    ) -> tuple[list[Post], int]:
        """分页查询岗位列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[Post], int]: (岗位列表, 总数)
        """
        stmt = select(Post)

        if query.post_name:
            stmt = stmt.where(Post.post_name.contains(query.post_name))
        if query.status is not None:
            stmt = stmt.where(Post.status == query.status)
        if query.dept_ids is not None and len(query.dept_ids)>0:
            stmt = stmt.where(Post.dept_id.in_(query.dept_ids))

        # 获取总数
        count_stmt = select(func.count()).select_from(Post)
        if query.post_name:
            count_stmt = count_stmt.where(Post.post_name.contains(query.post_name))
        if query.status is not None:
            count_stmt = count_stmt.where(Post.status == query.status)
        if query.dept_ids is not None:
            count_stmt = count_stmt.where(Post.dept_id.in_(query.dept_ids))
        
        total_result = await self.db_session.execute(count_stmt)
        total = total_result.scalar() or 0

        # 分页查询
        offset = (query.page_num - 1) * query.page_size
        stmt = stmt.order_by(Post.sort.asc(), Post.id.desc()).offset(offset).limit(query.page_size)
        
        result = await self.db_session.execute(stmt)
        posts = list(result.scalars().all())

        return posts, total

    async def create_post(self, post_data: dict) -> Post:
        """创建岗位

        Args:
            post_data: 岗位数据字典

        Returns:
            Post: 创建后的岗位对象
        """
        post = Post(**post_data)
        self.db_session.add(post)
        await self.db_session.flush()
        await self.db_session.refresh(post)
        return post

    async def update_post(self, post_id: int, post_data: dict) -> None:
        """更新岗位

        Args:
            post_id: 岗位ID
            post_data: 更新数据字典
        """
        stmt = (
            update(Post)
            .where(Post.id == post_id)
            .values(**post_data)
        )
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def delete_post(self, post_id: int) -> None:
        """删除岗位

        Args:
            post_id: 岗位ID
        """
        stmt = delete(Post).where(Post.id == post_id)
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def batch_delete_post(self, post_ids: list[int]) -> None:
        """批量删除岗位

        Args:
            post_ids: 岗位ID列表
        """
        if not post_ids:
            return

        stmt = delete(Post).where(Post.id.in_(post_ids))
        await self.db_session.execute(stmt)
        await self.db_session.flush()

    async def get_posts_bind_roles(self, post_ids: list[int], role_status: int | None = None) -> list[Role]:
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
            .join(PostRole, PostRole.role_id == Role.id)
            .where(PostRole.post_id.in_(post_ids))
        )

        if role_status is not None:
            stmt = stmt.where(Role.status == role_status)

        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())

    async def bind_roles_to_post(self, post_id: int, role_ids: list[int]) -> None:
        """批量绑定岗位角色关联

        Args:
            post_id: 岗位ID
            role_ids: 要绑定的角色ID列表
        """
        if not role_ids:
            return

        role_relations = [
            {"post_id": post_id, "role_id": role_id}
            for role_id in set(role_ids)
        ]

        insert_stmt = insert(PostRole).values(role_relations)
        await self.db_session.execute(insert_stmt)

    async def unbind_roles_from_post(self, post_id: int, role_ids: list[int]) -> None:
        """批量解绑岗位角色关联

        Args:
            post_id: 岗位ID
            role_ids: 要解绑的角色ID列表
        """
        if not role_ids:
            return

        delete_stmt = (
            delete(PostRole)
            .where(
                PostRole.post_id == post_id,
                PostRole.role_id.in_(role_ids)
            )
        )
        await self.db_session.execute(delete_stmt)

    async def list_posts_by_dept_id(self, dept_id: int) -> list[Post]:
        """根据部门ID查询部门下的所有岗位

        Args:
            dept_id: 部门ID

        Returns:
            list[Post]: 部门下的岗位列表
        """
        if dept_id is None:
            return []

        stmt = select(Post).where(Post.dept_id == dept_id)
        result = await self.db_session.execute(stmt)
        return list(result.scalars().all())