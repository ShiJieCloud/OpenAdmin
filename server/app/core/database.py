from sqlalchemy.engine.url import URL
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import event

from app.config.database import database_config
from contextlib import asynccontextmanager
from typing import AsyncGenerator
from pgvector.asyncpg import register_vector

# ------------------------------
# 异步引擎（postgresql+asyncpg）：业务API、ORM、pgvector向量读写
# ------------------------------
ASYNC_DB_URL = URL.create(
    drivername="postgresql+asyncpg",
    username=database_config.USER,
    password=database_config.PASSWORD,
    host=database_config.HOST,
    port=database_config.PORT,
    database=database_config.NAME,
)

async_engine = create_async_engine(
    ASYNC_DB_URL,
    echo=database_config.DEBUG,
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW,
    pool_pre_ping=True,       # 检测断开连接，生产建议开启
    pool_recycle=1800,        # 回收空闲连接，避免pg长连接断开
)

# ------------------------------
# 同步引擎（postgresql+psycopg）：供给 LangChain SQLDatabaseToolkit
# ------------------------------
SYNC_DB_URL = URL.create(
    drivername="postgresql+psycopg",
    username=database_config.USER,
    password=database_config.PASSWORD,
    host=database_config.HOST,
    port=database_config.PORT,
    database=database_config.NAME,
)

sync_engine = create_engine(
    SYNC_DB_URL,
    echo=database_config.DEBUG,
    pool_size=database_config.POOL_SIZE,
    max_overflow=database_config.MAX_OVERFLOW,
    pool_pre_ping=True,
    pool_recycle=1800,
)

# ------------------------------
# 异步会话工厂 FastAPI依赖注入
# ------------------------------
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


# FastAPI 依赖获取会话
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
