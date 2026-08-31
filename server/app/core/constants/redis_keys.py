class RedisKey:
    """
    Redis 键名常量定义
    统一管理所有 Redis 键名，避免硬编码字符串
    """

    # ==================== 统一前缀 ====================
    PREFIX = "open_admin"

    # ==================== 认证授权相关 ====================
    REFRESH_TOKEN_PREFIX = "refresh_token"
    ACCOUNT_LOCK_PREFIX = "account_lock"
    CAPTCHA_PREFIX = "captcha"
    ONLINE_USER_PREFIX = "online_user"
    ONLINE_USER_ZSET_PREFIX = "online_user_zset"

    # ==================== AI 对话相关 ====================
    AI_SESSIONS_PREFIX = "ai_sessions"   # 会话列表索引（ZSet）
    AI_SESSION_PREFIX = "ai_session"     # 会话元数据（Hash）
    AI_MESSAGES_PREFIX = "ai_messages"    # 消息历史（List）

class RedisKeyTemplate:
    """
    Redis 键名模板生成器
    统一生成带参数的 Redis 键名
    """

    @staticmethod
    def refresh_token(user_id: int) -> str:
        """刷新令牌缓存键"""
        return f"{RedisKey.PREFIX}:{RedisKey.REFRESH_TOKEN_PREFIX}:{user_id}"

    @staticmethod
    def account_lock(user_id: int) -> str:
        """账号锁定标记键（值：锁定结束时间戳）"""
        return f"{RedisKey.PREFIX}:{RedisKey.ACCOUNT_LOCK_PREFIX}:{user_id}"

    @staticmethod
    def captcha(captcha_id: str) -> str:
        """验证码缓存键（值：验证码字符串）"""
        return f"{RedisKey.PREFIX}:{RedisKey.CAPTCHA_PREFIX}:{captcha_id}"

    @staticmethod
    def online_user(user_id: int) -> str:
        """在线用户缓存键（值：用户信息 JSON 字符串）"""
        return f"{RedisKey.PREFIX}:{RedisKey.ONLINE_USER_PREFIX}:{user_id}"

    @staticmethod
    def online_user_zset() -> str:
        """在线用户 ZSET 缓存键（值：用户ID 列表）"""
        return f"{RedisKey.PREFIX}:{RedisKey.ONLINE_USER_ZSET_PREFIX}"

    @staticmethod
    def ai_sessions(user_id: int) -> str:
        """AI 会话列表索引键（ZSet，score=更新时间戳）"""
        return f"{RedisKey.PREFIX}:{RedisKey.AI_SESSIONS_PREFIX}:{user_id}"

    @staticmethod
    def ai_session(session_id: str) -> str:
        """AI 会话元数据键（Hash：title/user_id/时间戳）"""
        return f"{RedisKey.PREFIX}:{RedisKey.AI_SESSION_PREFIX}:{session_id}"

    @staticmethod
    def ai_messages(session_id: str) -> str:
        """AI 会话消息历史键（List，元素为消息 JSON）"""
        return f"{RedisKey.PREFIX}:{RedisKey.AI_MESSAGES_PREFIX}:{session_id}"