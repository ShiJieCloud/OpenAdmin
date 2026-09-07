from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import text

from app.core.database import async_engine
from app.core.redis import redis_client
from app.core.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理

    启动时检测数据库、Redis 连通性（不自动建表，表结构统一由 Alembic 迁移管理），
    连接失败则快速失败、终止启动；关闭时释放数据库与 Redis 连接。
    """
    # 启动时：数据库连通性检测（SELECT 1 验证连接可用，不执行任何建表操作）
    logger.info("正在检测数据库连接...")
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        logger.info("数据库连接成功！")
    except Exception as e:
        logger.error(f"数据库连接失败，请检查数据库配置与服务状态：{e}")
        raise

    logger.info("正在初始化Redis连接...")
    await redis_client.init()
    logger.info("Redis连接初始化完成！")
    
    yield
    
    # 关闭时执行
    logger.info("正在关闭数据库连接...")
    await async_engine.dispose()
    logger.info("数据库连接已关闭！")

    logger.info("正在关闭Redis连接...")
    await redis_client.close()
    logger.info("Redis连接已关闭！")
