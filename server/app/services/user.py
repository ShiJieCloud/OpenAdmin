from app.core.constants import RedisKeyTemplate, TimeSec
from app.core.enums import RespCodeEnum
from app.core.exceptions import BusinessError
from app.core.security import verify_password, create_tokens
from app.crud.user import UserCRUD
from app.models.user import User
from app.schemas.auth import PasswordLoginRequest, TokenResponse
from app.services.base import BaseService
from app.core.redis import RedisClient
from app.config import auth_config


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
