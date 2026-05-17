import contextvars
from typing import Any, Dict

from pydantic import BaseModel, Field


class ContextData(BaseModel):
    """
    上下文数据模型
    统一封装所有上下文字段信息
    """

    current_user_id: int | None = Field(default=None, description="当前登录用户ID")
    current_username: str | None = Field(default=None, description="当前登录用户名")
    trace_id: str | None = Field(default=None, description="请求唯一ID")
    client_ip: str | None = Field(default=None, description="客户端IP地址")
    request_method: str | None = Field(default=None, description="请求方法")
    request_path: str | None = Field(default=None, description="请求路径")


class AppContext:
    """
    企业级全局上下文工具类
    所有获取/设置必须走这里，统一规范
    """

    _context_var = contextvars.ContextVar[ContextData]("app_context", default=ContextData())

    @classmethod
    def _get_context(cls) -> ContextData:
        """获取当前上下文数据对象（内部方法）"""
        return cls._context_var.get()
  
    @classmethod
    def clear(cls) -> None:
        """清空当前上下文，重置为初始状态"""
        cls._context_var.set(ContextData())

    @classmethod
    def get_all(cls) -> Dict[str, Any]:
        """获取完整上下文字典副本
        
        Returns:
            所有上下文数据的字典形式
        """
        ctx = cls._get_context()
        return ctx.model_dump()

    @classmethod
    def set_current_user_id(cls, user_id: int | None) -> None:
        """设置当前登录用户ID
        
        Args:
            user_id: 用户ID
        """
        ctx = cls._get_context()
        ctx.current_user_id = user_id
        cls._context_var.set(ctx)
    
    @classmethod
    def get_current_user_id(cls) -> int | None:
        """获取当前登录用户ID
        
        Returns:
            当前登录用户ID
        """
        ctx = cls._get_context()
        return ctx.current_user_id

    @classmethod
    def set_trace_id(cls, trace_id: str | None) -> None:
        """设置请求唯一ID
        
        Args:
            trace_id: 请求唯一ID
        """
        ctx = cls._get_context()
        ctx.trace_id = trace_id
        cls._context_var.set(ctx)
    
    @classmethod
    def get_trace_id(cls) -> str | None:
        """获取请求唯一ID
        
        Returns:
            请求唯一ID
        """
        ctx = cls._get_context()
        return ctx.trace_id

    @classmethod
    def set_current_username(cls, username: str | None) -> None:
        """设置当前登录用户名
        
        Args:
            username: 用户名
        """
        ctx = cls._get_context()
        ctx.current_username = username
        cls._context_var.set(ctx)
    
    @classmethod
    def get_current_username(cls) -> str | None:
        """获取当前登录用户名
        
        Returns:
            当前登录用户名
        """
        ctx = cls._get_context()
        return ctx.current_username

    @classmethod
    def set_client_ip(cls, client_ip: str | None) -> None:
        """设置客户端IP地址
        
        Args:
            client_ip: 客户端IP地址
        """
        ctx = cls._get_context()
        ctx.client_ip = client_ip
        cls._context_var.set(ctx)
    
    @classmethod
    def get_client_ip(cls) -> str | None:
        """获取客户端IP地址
        
        Returns:
            客户端IP地址
        """
        ctx = cls._get_context()
        return ctx.client_ip

    @classmethod
    def set_request_method(cls, request_method: str | None) -> None:
        """设置请求方法
        
        Args:
            request_method: 请求方法
        """
        ctx = cls._get_context()
        ctx.request_method = request_method
        cls._context_var.set(ctx)
    
    @classmethod
    def get_request_method(cls) -> str | None:
        """获取请求方法
        
        Returns:
            请求方法
        """
        ctx = cls._get_context()
        return ctx.request_method

    @classmethod
    def set_request_path(cls, request_path: str | None) -> None:
        """设置请求路径
        
        Args:
            request_path: 请求路径
        """
        ctx = cls._get_context()
        ctx.request_path = request_path
        cls._context_var.set(ctx)
    
    @classmethod
    def get_request_path(cls) -> str | None:
        """获取请求路径
        
        Returns:
            请求路径
        """
        ctx = cls._get_context()
        return ctx.request_path