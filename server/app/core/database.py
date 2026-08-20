from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine

from app.config.database import database_config
from contextlib import asynccontextmanager
from typing import AsyncGenerator

# 创建数据库URL
ASYNC_DB_URL = URL.create(
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
async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=database_config.DEBUG,
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW
)

# 创建同步数据库URL（使用同步驱动）
SYNC_DB_URL = URL.create(
    drivername="mysql+pymysql",
    username=database_config.USER,
    password=database_config.PASSWORD,
    host=database_config.HOST,
    port=database_config.PORT,
    database=database_config.NAME,
    query={
        "charset": database_config.CHARSET,
    }
)

# 创建同步引擎（用于 LangChain SQLDatabaseToolkit）
sync_engine = create_engine(
    SYNC_DB_URL,
    echo=database_config.DEBUG,
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW
)

# 创建异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

@asynccontextmanager
async def get_async_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    🔥 异步数据库会话
    - 支持非接口上下文: async with get_async_db_session() as db:
    - 自动提交 / 回滚
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
