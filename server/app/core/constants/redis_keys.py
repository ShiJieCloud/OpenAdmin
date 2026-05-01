class RedisKey:
    """
    Redis 键名常量定义
    统一管理所有 Redis 键名，避免硬编码字符串
    """

    # ==================== 统一前缀 ====================
    PREFIX = "open_admin"

    # ==================== 认证授权相关 ====================
    REFRESH_TOKEN = "refresh_token"

class RedisKeyTemplate:
    """
    Redis 键名模板生成器
    统一生成带参数的 Redis 键名
    """

    @staticmethod
    def refresh_token(user_id: int) -> str:
        """刷新令牌缓存键"""
        return f"{RedisKey.PREFIX}:{RedisKey.REFRESH_TOKEN}:{user_id}"
