from datetime import datetime

from app.core.context import AppContext
from app.core.enums import RespCodeEnum, UserStatusEnum
from app.core.exceptions import BusinessError
from app.core.security import get_password_hash
from app.crud import UserApplyCRUD, UserCRUD, PostCRUD
from app.models import UserApply
from app.schemas.auth import RegisterRequest
from app.schemas.user_apply import UserApplyListQueryRequest, UserApplyRejectRequest, UserApplyPassRequest
from app.services.base import BaseService


class UserApplyService(BaseService):
    """用户注册申请服务类"""

    def __init__(self, db_session):
        super().__init__(db_session)
        self.apply_crud = UserApplyCRUD(db_session)
        self.user_crud = UserCRUD(db_session)
        self.post_crud = PostCRUD(db_session)

    async def create_apply(self, req: RegisterRequest) -> UserApply:
        """提交用户注册申请

        公开接口，无需登录。仅校验唯一性并写入申请表（status=0 待审核），
        不创建正式系统用户。待管理员审批通过后再由 pass_apply 创建 sys_user 记录。
        短信验证码校验待接入短信服务后补充。

        Args:
            req: 注册请求

        Returns:
            创建后的申请对象

        Raises:
            BusinessError: 用户名已有正式账号、手机号已被注册、已有待审核申请
        """
        # 1. 校验用户名是否已被正式账号占用
        existing_user = await self.user_crud.get_user(username=req.username)
        if existing_user is not None:
            raise BusinessError(RespCodeEnum.USER_APPLY_USER_EXIST)

        # 2. 校验手机号是否已被正式账号占用
        if req.phone:
            existing_user = await self.user_crud.get_user(phone=req.phone)
            if existing_user is not None:
                raise BusinessError(RespCodeEnum.PHONE_EXIST)

        # 3. 校验是否已有待审核申请，避免重复提交
        pending_apply = await self.apply_crud.get_pending_apply(req.username)
        if pending_apply is not None:
            raise BusinessError(RespCodeEnum.USER_APPLY_HAS_PENDING)

        # 4. 密码加密
        hashed_password = get_password_hash(req.password)

        # 5. 创建注册申请（status=0 待审核）
        apply_data = {
            "username": req.username,
            "phone": req.phone,
            "password": hashed_password,
            "status": 0,
        }
        return await self.apply_crud.create_apply(apply_data)

    async def get_apply_list(self, query: UserApplyListQueryRequest) -> tuple[list[UserApply], int, int, int]:
        """分页查询用户注册申请列表

        Args:
            query: 查询条件

        Returns:
            (申请列表, 总条数, 总页数, 当前页码)
        """
        return await self.apply_crud.get_apply_list(query)

    async def get_apply(self, apply_id: int) -> UserApply:
        """获取申请详情

        Args:
            apply_id: 申请ID

        Returns:
            申请对象

        Raises:
            BusinessError: 申请不存在
        """
        apply = await self.apply_crud.get_apply(apply_id)
        if apply is None:
            raise BusinessError(RespCodeEnum.USER_APPLY_NOT_EXIST)
        return apply

    async def pass_apply(self, apply_id: int, req: UserApplyPassRequest) -> UserApply:
        """审批通过：更新申请状态并创建对应系统用户

        审批通过时会复用申请表中已加密的密码，在 sys_user 表创建一条正式用户记录，
        状态默认为正常，并根据上送的部门ID和岗位ID列表完成用户-部门归属和岗位绑定。
        岗位必须全部属于上送部门，否则拒绝。
        整个流程在数据库事务内完成（依赖注入层统一提交）。

        Args:
            apply_id: 申请ID
            req: 审批通过请求，包含部门ID和岗位ID列表

        Returns:
            更新后的申请对象

        Raises:
            BusinessError: 申请不存在、申请已处理、用户名/手机号已被占用、
                          岗位不存在、岗位部门与上送部门不一致
        """
        # 1. 校验申请是否存在且为待审核状态
        apply = await self.get_apply(apply_id)
        if apply.status != 0:
            raise BusinessError(RespCodeEnum.USER_APPLY_ALREADY_PROCESSED)

        # 2. 校验用户名是否已被正式用户占用
        existing_user = await self.user_crud.get_user(username=apply.username)
        if existing_user is not None:
            raise BusinessError(RespCodeEnum.USERNAME_EXIST)

        # 3. 校验手机号是否已被占用
        if apply.phone:
            existing_user = await self.user_crud.get_user(phone=apply.phone)
            if existing_user is not None:
                raise BusinessError(RespCodeEnum.PHONE_EXIST)

        # 4. 校验岗位必须属于上送部门
        await self._validate_posts_dept(req.post_ids, req.dept_id)

        # 5. 创建正式用户（密码沿用申请表中的加密密码，避免重复加密）
        user_data = {
            "username": apply.username,
            "password": apply.password,
            "phone": apply.phone,
            "status": UserStatusEnum.NORMAL,
            "dept_id": req.dept_id,
        }
        user = await self.user_crud.create_user(user_data)

        # 6. 绑定岗位
        if req.post_ids:
            await self.user_crud.bind_posts_to_user(user.id, req.post_ids)

        # 7. 更新申请状态为已通过
        audit_user_id = AppContext.get_current_user_id()
        await self.apply_crud.update_audit_status(
            apply_id=apply_id,
            status=1,
            audit_user_id=audit_user_id,
            audit_time=datetime.now(),
        )

        # 8. 重新获取并返回更新后的申请
        return await self.apply_crud.get_apply(apply_id)

    async def _validate_posts_dept(self, post_ids: list[int], dept_id: int) -> None:
        """校验岗位的部门ID是否与上送部门一致

        Args:
            post_ids: 岗位ID列表
            dept_id: 上送部门ID

        Raises:
            BusinessError: 岗位不存在或岗位部门与上送部门不一致
        """
        if not post_ids:
            return

        for post_id in post_ids:
            post = await self.post_crud.get_post(post_id)
            if not post:
                raise BusinessError(RespCodeEnum.POST_NOT_EXIST)
            if post.dept_id != dept_id:
                raise BusinessError(RespCodeEnum.USER_POST_DEPT_MISMATCH)

    async def reject_apply(self, apply_id: int, req: UserApplyRejectRequest) -> UserApply:
        """审批拒绝：更新申请状态为已拒绝，记录拒绝原因

        Args:
            apply_id: 申请ID
            req: 拒绝请求（包含原因）

        Returns:
            更新后的申请对象

        Raises:
            BusinessError: 申请不存在、申请已处理
        """
        # 1. 校验申请是否存在且为待审核状态
        apply = await self.get_apply(apply_id)
        if apply.status != 0:
            raise BusinessError(RespCodeEnum.USER_APPLY_ALREADY_PROCESSED)

        # 2. 更新申请状态为已拒绝
        audit_user_id = AppContext.get_current_user_id()
        await self.apply_crud.update_audit_status(
            apply_id=apply_id,
            status=2,
            audit_user_id=audit_user_id,
            audit_time=datetime.now(),
            audit_reason=req.reason,
        )

        # 3. 重新获取并返回更新后的申请
        return await self.apply_crud.get_apply(apply_id)
