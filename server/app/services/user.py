from app.config import auth_config
from app.core.constants import RedisKeyTemplate, TimeSec
from app.core.enums import RespCodeEnum, UserStatusEnum
from app.core.exceptions import BusinessError
from app.core.security import verify_password, create_tokens, verify_refresh_token
from app.crud.user import UserCRUD
from app.models.user import User
from app.schemas.auth import PasswordLoginRequest, RefreshTokenRequest, TokenResponse
from app.services.base import BaseService
from app.core.redis import RedisClient


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

        # 1. 校验用户名是否存在
        user = await self.user_crud.get_user(username=req.username)
        if user is None:
            raise BusinessError(RespCodeEnum.USER_NOT_EXIST)
        
        # 2. 校验密码是否正确
        if not verify_password(req.password, user.password):
            raise BusinessError(RespCodeEnum.PWD_VERIFY_FAIL)

        # 3. 生成 JWT 令牌
        access_token, refresh_token = create_tokens(user.id)
        
        # 4. 存储刷新令牌到 Redis
        await self.redis_client.set(
            RedisKeyTemplate.refresh_token(user.id),
            refresh_token,
            auth_config.JWT_REFRESH_TOKEN_EXPIRE_DAYS * TimeSec.DAY
        )

        # 5. 返回令牌
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
