from app.core.enums import RespCodeEnum, RoleStatusEnum
from app.core.exceptions import BusinessError
from app.crud.post import PostCRUD
from app.models import Role
from app.schemas.post import PostInfoResponse, PostCreateRequest, PostUpdateRequest, PostListQueryRequest
from app.services.base import BaseService


class PostService(BaseService):
    """岗位服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.post_crud = PostCRUD(db_session)

    async def get_post(self, post_id: int) -> PostInfoResponse:
        """获取岗位详情

        Args:
            post_id: 岗位ID

        Returns:
            PostInfoResponse: 岗位信息响应对象

        Raises:
            BusinessError: 岗位不存在
        """
        post = await self.post_crud.get_post(post_id)
        if not post:
            raise BusinessError(RespCodeEnum.POST_NOT_EXIST)
        return PostInfoResponse.model_validate(post)

    async def list_posts(
        self,
        query: PostListQueryRequest
    ) -> tuple[list[PostInfoResponse], int]:
        """分页查询岗位列表

        Args:
            query: 查询条件

        Returns:
            tuple[list[PostInfoResponse], int]: (岗位列表, 总数)
        """
        posts, total = await self.post_crud.list_posts(query)
        return [PostInfoResponse.model_validate(post) for post in posts], total

    async def create_post(self, req: PostCreateRequest) -> PostInfoResponse:
        """创建岗位

        Args:
            req: 创建岗位请求

        Returns:
            PostInfoResponse: 创建后的岗位信息响应对象

        Raises:
            BusinessError: 岗位名称已存在 / 岗位编码已存在
        """
        # 校验岗位名称是否已存在
        existing_post = await self.post_crud.get_post_by_name(req.post_name)
        if existing_post:
            raise BusinessError(RespCodeEnum.POST_NAME_EXIST)

        post_data = req.model_dump()
        post = await self.post_crud.create_post(post_data)
        return PostInfoResponse.model_validate(post)

    async def update_post(self, req: PostUpdateRequest) -> PostInfoResponse:
        """更新岗位

        Args:
            req: 更新岗位请求

        Returns:
            PostInfoResponse: 更新后的岗位信息响应对象

        Raises:
            BusinessError: 岗位不存在 / 岗位名称已存在 / 岗位编码已存在
        """
        # 校验岗位是否存在
        post = await self.post_crud.get_post(req.post_id)
        if not post:
            raise BusinessError(RespCodeEnum.POST_NOT_EXIST)

        # 校验岗位名称是否已存在（排除自身）
        if req.post_name and req.post_name != post.post_name:
            existing_post = await self.post_crud.get_post_by_name(
                req.post_name, exclude_id=req.post_id
            )
            if existing_post:
                raise BusinessError(RespCodeEnum.POST_NAME_EXIST)

        # 构造更新数据
        update_data = req.model_dump(exclude_unset=True, exclude={"post_id"})
        if update_data:
            await self.post_crud.update_post(req.post_id, update_data)
            post = await self.post_crud.get_post(req.post_id)

        return PostInfoResponse.model_validate(post)

    async def delete_post(self, post_id: int) -> None:
        """删除岗位

        Args:
            post_id: 岗位ID

        Raises:
            BusinessError: 岗位不存在
        """
        post = await self.post_crud.get_post(post_id)
        if not post:
            raise BusinessError(RespCodeEnum.POST_NOT_EXIST)

        await self.post_crud.delete_post(post_id)

    async def batch_delete_post(self, post_ids: list[int]) -> None:
        """批量删除岗位

        Args:
            post_ids: 岗位ID列表

        Raises:
            BusinessError: 岗位不存在
        """
        if not post_ids:
            return

        # 校验所有岗位是否存在
        for post_id in post_ids:
            post = await self.post_crud.get_post(post_id)
            if not post:
                raise BusinessError(RespCodeEnum.POST_NOT_EXIST)

        await self.post_crud.batch_delete_post(post_ids)

    async def get_posts_bind_roles(self, post_ids: list[int], role_status: RoleStatusEnum | None = None) -> list[Role]:
        """
        批量获取多个岗位关联的角色列表（去重）

        Args:
            post_ids: 岗位ID列表

        Returns:
            list[Role]: 去重后的角色列表
        """
        return await self.post_crud.get_posts_bind_roles(post_ids, role_status)

    async def assign_roles_to_post(self, post_id: int, role_ids: list[int]) -> list[int]:
        """对比差异分配角色给岗位

        前端传入岗位调整后的所有角色ID
        Service层对比差异：
        - 数据库没有，前端有 → 调用CRUD新增
        - 数据库有，前端没有 → 调用CRUD删除
        - 两边都有 → 保持不变

        Args:
            post_id: 岗位ID
            role_ids: 前端最终的角色ID列表

        Returns:
            list[int]: 分配后的角色ID列表
        """
        post = await self.post_crud.get_post(post_id)
        if not post:
            raise BusinessError(RespCodeEnum.POST_NOT_EXIST)

        existing_roles = await self.post_crud.get_posts_bind_roles([post_id])
        existing_role_ids = set(map(lambda x: x.id, existing_roles))
        new_set = set(role_ids)

        to_add = new_set - existing_role_ids
        to_remove = existing_role_ids - new_set

        if to_remove:
            await self.post_crud.unbind_roles_from_post(post_id, list(to_remove))

        if to_add:
            await self.post_crud.bind_roles_to_post(post_id, list(to_add))

        final_bind_roles = await self.post_crud.get_posts_bind_roles([post_id])
        
        return [role.id for role in final_bind_roles]
