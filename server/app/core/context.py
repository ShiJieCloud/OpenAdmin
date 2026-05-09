import contextvars
from typing import Any, Dict

from pydantic import BaseModel, Field


class ContextData(BaseModel):
    """
    上下文数据模型
    统一封装所有上下文字段信息
    """

    current_user_id: int | None = Field(default=None, description="当前登录用户ID")
    trace_id: str | None = Field(default=None, description="请求唯一ID")


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
