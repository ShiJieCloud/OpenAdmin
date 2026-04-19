from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.core.database import engine
from app.models import BaseModel


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理
    
    在应用启动时创建数据库表，在应用关闭时关闭数据库连接
    """
    # 启动时执行
    print("正在初始化数据库...")
    async with engine.begin() as conn:
        await conn.run_sync(BaseModel.metadata.create_all)
    print("数据库初始化完成！")
    
    yield
    
    # 关闭时执行
    print("正在关闭数据库连接...")
    await engine.dispose()
    print("数据库连接已关闭！")
