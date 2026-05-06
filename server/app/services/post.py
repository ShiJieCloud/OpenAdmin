from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.crud.post import PostCRUD
from app.models import Post, Role
from app.services.base import BaseService


class PostService(BaseService):
    """岗位服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.post_crud = PostCRUD(db_session)

    async def get_post(self, post_id: int) -> Post:
        """获取岗位详情

        Args:
            post_id: 岗位ID

        Returns:
            Post: 岗位对象

        Raises:
            BusinessError: 岗位不存在
        """
        post = await self.post_crud.get_post(post_id)
        if not post:
            raise BusinessError(RespCodeEnum.POST_NOT_EXIST)
        return post

    async def get_posts_roles(self, post_ids: list[int]) -> list[Role]:
        """
        批量获取多个岗位关联的角色列表（去重）

        Args:
            post_ids: 岗位ID列表

        Returns:
            list[Role]: 去重后的角色列表
        """
        return await self.post_crud.get_posts_roles(post_ids)