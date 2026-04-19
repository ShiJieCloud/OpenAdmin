from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.config.database import database_config

# 创建数据库URL
DB_URL = URL.create(
    drivername="mysql+asyncmy",
    username=database_config.USER,
    password=database_config.PASSWORD,
    host=database_config.HOST,
    port=database_config.PORT,
    database=database_config.NAME,
    query={
        "charset": database_config.CHARSET,
        "sql_mode": "STRICT_TRANS_TABLES",
    }
)

# 创建异步引擎
engine = create_async_engine(
    DB_URL,
    echo=database_config.DEBUG,
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)
