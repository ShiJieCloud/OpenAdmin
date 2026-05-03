from app.config import auth_config
from app.core.constants import RedisKeyTemplate, TimeSec
from app.core.enums import RespCodeEnum, UserStatusEnum
from app.core.exceptions import BusinessError
from app.core.security import verify_password, create_tokens, verify_refresh_token, get_password_hash
from app.crud import UserCRUD
from app.models import User, Role
from app.schemas.auth import PasswordLoginRequest, RefreshTokenRequest, TokenResponse
from app.schemas.user import UserCreateRequest, UserResetPasswordRequest
from app.services.base import BaseService
from app.core.redis import RedisClient
from datetime import datetime


class UserService(BaseService):
    """用户服务类"""

    def __init__(self, db_session, redis_client: RedisClient):
        super().__init__(db_session)
        self.user_crud = UserCRUD(db_session)
        self.redis_client = redis_client

    async def get_user(self, 
        id: int | None = None,
        username: str | None = None,
        email: str | None = None,
        phone: str | None = None
    ) -> User:
        """根据ID、用户名、邮箱或手机号获取用户

        Args:
            id: 用户ID
            username: 用户名
            email: 邮箱
            phone: 手机号

        Returns:
            用户对象
        """
        
        # 1. 至少传入一个查询条件
        if id is None and username is None and email is None and phone is None:
            raise BusinessError(RespCodeEnum.QUERY_CONDITION_INVALID)

        # 2. 查询用户信息
        user = await self.user_crud.get_user(id, username, email, phone)
        if user is None:
            raise BusinessError(RespCodeEnum.USER_NOT_EXIST)

        return user

    async def login_password(self, req: PasswordLoginRequest) -> TokenResponse:
        """账号密码登录"""

        # 1. 查询用户
        user = await self.user_crud.get_user(username=req.username)
        if user is None:
            raise BusinessError(RespCodeEnum.USER_NOT_EXIST)

        # 2. 检查账户状态
        if user.status == UserStatusEnum.LOCKED:
            # 锁定状态判断是否要自动解锁
            is_locked = await self.redis_client.exists(RedisKeyTemplate.account_lock(user.id))
            if is_locked:
                raise BusinessError(RespCodeEnum.ACCOUNT_LOCKED)
            # Redis 锁已过期，自动解锁
            await self.user_crud.reset_user_login_status(user.id)
        elif user.status != UserStatusEnum.NORMAL:
            # 其它状态直接报错
            raise BusinessError(RespCodeEnum.ACCOUNT_STATUS_ABNORMAL)

        # 3. 密码校验
        if not verify_password(req.password, user.password):

            # 失败次数 +1
            await self.user_crud.increment_login_fail_count(user.id)

             # 计算剩余次数，包含当前失败次数（SQLAlchemy 会自动同步 Session 内 UPDATE 后的属性）
            remaining_attempts = auth_config.MAX_LOGIN_ATTEMPTS - user.login_fail_count
            
            #  达到上限 → 锁定账号
            if remaining_attempts <= 0:

                # 密码错误次数超过最大尝试次数，锁定账号
                await self.user_crud.lock_user(user.id)

                # 设置 Redis 锁，过期时间为 LOCK_DURATION 秒
                await self.redis_client.set(
                    RedisKeyTemplate.account_lock(user.id),
                    datetime.now().timestamp(),
                    auth_config.ACCOUNT_LOCK_DURATION_MINUTES * TimeSec.MINUTE
                )
                raise BusinessError(RespCodeEnum.ACCOUNT_LOCKED)

            # 未达上限 → 返回剩余次数
            raise BusinessError(RespCodeEnum.PWD_VERIFY_FAIL, count=remaining_attempts)

        # 4. 登录成功 → 重置所有登录状态
        await self.user_crud.reset_user_login_status(user.id)

        # 5. 生成令牌
        access_token, refresh_token = create_tokens(user.id)
        await self.redis_client.set(
            RedisKeyTemplate.refresh_token(user.id),
            refresh_token,
            auth_config.JWT_REFRESH_TOKEN_EXPIRE_DAYS * TimeSec.DAY
        )

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=auth_config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * TimeSec.MINUTE
        )

    async def refresh_token(self, req: RefreshTokenRequest) -> TokenResponse:
        """刷新令牌
        
        Args:
            req: 刷新令牌请求对象
            
        Returns:
            TokenResponse: 新的访问令牌和刷新令牌响应对象
        """
        # 1. 验证 refresh_token 签名和有效期
        payload = verify_refresh_token(req.refresh_token)
        user_id = int(payload.sub)

        # 2. 从 Redis 获取存储的 refresh_token
        stored_token = await self.redis_client.get(RedisKeyTemplate.refresh_token(user_id))
        
        # 3. 校验令牌是否匹配（防止复用泄露的令牌）
        if not stored_token or stored_token != req.refresh_token:
            raise BusinessError(RespCodeEnum.TOKEN_INVALID)

        # 4. 校验用户状态
        user = await self.user_crud.get_user(id=user_id)
        if user is None:
            raise BusinessError(RespCodeEnum.USER_NOT_EXIST)
        if not UserStatusEnum.is_normal(user.status):
            # 用户状态异常，拒绝刷新令牌，删除 refresh_token
            await self.redis_client.delete(RedisKeyTemplate.refresh_token(user_id))
            raise BusinessError(RespCodeEnum.LOGIN_EXPIRED)

        # 5. 生成新的令牌对
        new_access_token, new_refresh_token = create_tokens(user_id)

        # 6. 更新 Redis 中的 refresh_token
        await self.redis_client.set(
            RedisKeyTemplate.refresh_token(user_id),
            new_refresh_token,
            auth_config.JWT_REFRESH_TOKEN_EXPIRE_DAYS * TimeSec.DAY
        )

        # 7. 返回新令牌
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            expires_in=auth_config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * TimeSec.MINUTE
        )

    async def logout(self, user_id: int) -> None:
        """用户退出登录，销毁 Redis 中的刷新令牌
        
        Args:
            user_id: 用户ID
        """
        # 从 Redis 删除刷新令牌
        await self.redis_client.delete(RedisKeyTemplate.refresh_token(user_id))

    async def get_user_roles(self, user_id: int) -> list[Role]:
        """
        获取用户关联的角色列表
        """
        roles = await self.user_crud.get_user_roles(user_id)
        if not roles:
            return []
        
        return roles

    async def create_user(self, req: UserCreateRequest) -> User:
        """
        创建新用户

        :param req: 创建用户请求
        :return: 创建后的用户对象
        """
        # 校验用户名是否已存在
        existing_user = await self.user_crud.get_user(username=req.username)
        if existing_user:
            raise BusinessError(RespCodeEnum.USERNAME_EXIST)

        # 校验邮箱是否已存在
        if req.email:
            existing_user = await self.user_crud.get_user(email=req.email)
            if existing_user:
                raise BusinessError(RespCodeEnum.EMAIL_EXIST)

        # 校验手机号是否已存在
        if req.phone:
            existing_user = await self.user_crud.get_user(phone=req.phone)
            if existing_user:
                raise BusinessError(RespCodeEnum.PHONE_EXIST)

        # 密码加密
        hashed_password = get_password_hash(req.password)

        # 构建用户数据
        user_data = req.model_dump()
        user_data["password"] = hashed_password

        # 创建用户
        user = await self.user_crud.create_user(user_data)
        return user

    async def reset_user_password(self, req: UserResetPasswordRequest) -> None:
        """
        重置用户密码

        :param req: 重置密码请求
        :return: None
        """
        # 校验用户是否存在
        user = await self.user_crud.get_user(id=req.user_id)
        if user is None:
            raise BusinessError(RespCodeEnum.USER_NOT_EXIST)

        # 校验用户是否被软删除（0=未删除 1=已删除）
        if user.del_flag:
            raise BusinessError(RespCodeEnum.USER_DELETED)
        
        # 校验用户状态是否正常
        if not UserStatusEnum.is_normal(user.status):
            raise BusinessError(RespCodeEnum.USER_STATUS_INVALID)

        # 密码加密
        hashed_password = get_password_hash(req.new_password)

        # 更新密码
        await self.user_crud.update_user_password(req.user_id, hashed_password)
        
