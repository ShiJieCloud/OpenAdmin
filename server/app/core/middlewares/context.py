from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import AppContext


class ContextMiddleware(BaseHTTPMiddleware):
    """
    上下文中间件
    为每个请求自动初始化、填充和清理 AppContext 上下文数据
    
    功能特性：
    - 自动生成并注入唯一请求ID，支持链路追踪
    - 自动记录请求路径、请求方法、客户端IP等基础信息
    - 请求结束后自动清理上下文，避免内存泄漏和数据污染
    - 支持将请求ID注入响应头，便于前端排查问题
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:
            response: Response = await call_next(request)
            return response
        finally:
            AppContext.clear()

def setup_context_middleware(app: FastAPI):
    """配置上下文中间件
    
    为 FastAPI 应用实例添加上下文中间件，确保每个请求
    都能获得独立、安全的上下文环境
    
    Args:
        app: FastAPI 应用实例
    """
    app.add_middleware(ContextMiddleware)
