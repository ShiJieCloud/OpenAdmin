from pydantic import Field
from app.config.base import BaseConfig
from pydantic_settings import SettingsConfigDict


class RedisConfig(BaseConfig):
    """Redis配置类
    
    从环境变量中读取 Redis 配置，环境变量前缀为 REDIS_：
    1. REDIS_HOST: Redis 主机名，默认值为 localhost
    2. REDIS_PORT: Redis 端口号，默认值为 6379
    3. REDIS_PASSWORD: Redis 密码，默认值为空字符串
    4. REDIS_DB: Redis 数据库索引，默认值为 0
    5. REDIS_DECODE_RESPONSES: 是否解码响应，默认值为 True
    6. REDIS_SOCKET_CONNECT_TIMEOUT: 连接超时时间，默认值为 5 秒
    7. REDIS_SOCKET_TIMEOUT: 套接字超时时间，默认值为 10 秒
    8. REDIS_MAX_CONNECTIONS: 最大连接数，默认值为 50
    """
    HOST: str = Field(default="localhost", description="Redis 主机地址")
    PORT: int = Field(default=6379, description="Redis 端口")
    PASSWORD: str = Field(default="", description="Redis 密码")
    DB: int = Field(default=0, description="Redis 数据库索引")
    DECODE_RESPONSES: bool = Field(default=True, description="是否自动解码响应")
    SOCKET_CONNECT_TIMEOUT: int = Field(default=5, description="连接超时时间")
    SOCKET_TIMEOUT: int = Field(default=10, description="套接字超时时间")
    MAX_CONNECTIONS: int = Field(default=50, description="Redis 最大连接数")

    model_config = SettingsConfigDict(
        env_prefix="REDIS_"
    )


redis_config = RedisConfig()
