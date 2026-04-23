from typing import Generic, List, Optional
from pydantic import BaseModel, Field
from app.core.types import T


class BaseResponse(BaseModel):
    """基础响应模型"""
    code: str = Field(..., description="业务状态码")
    message: str = Field(..., description="提示信息")
    timestamp: int = Field(..., description="服务器当前毫秒时间戳")


class ApiResponse(BaseResponse, Generic[T]):
    """API 响应模型"""
    data: Optional[T] = Field(None, description="业务数据")


class PaginationData(BaseModel, Generic[T]):
    """分页数据模型"""
    records: List[T] = Field(..., description="当前页数据列表")
    total: int = Field(..., description="总条数")
    page_num: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页条数")
    pages: int = Field(..., description="总页数")


class PaginationResponse(BaseResponse, Generic[T]):
    """分页响应模型"""
    data: PaginationData[T] = Field(..., description="分页数据")
