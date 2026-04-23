from datetime import datetime
from typing import List, Optional

from app.schemas.base.response import ApiResponse, PaginationResponse, PaginationData
from .enums import RespCodeEnum
from .types import T


class ResponseBuilder:
    """响应构建器类
    
    使用类方法构建不同类型的响应对象
    """
    
    @classmethod
    def success(cls, data: Optional[T] = None, message: Optional[str] = None) -> ApiResponse[T]:
        """构建成功响应
        
        Args:
            data: 业务数据
            message: 提示信息，默认为 None，会使用响应码的默认提示信息
        
        Returns:
            ApiResponse 对象
        """
        return ApiResponse[T](
            code=RespCodeEnum.SUCCESS,
            message=message or RespCodeEnum.SUCCESS.msg,
            data=data,
            timestamp=int(datetime.now().timestamp() * 1000)
        )
    
    @classmethod
    def error(cls, code: RespCodeEnum, message: Optional[str] = None) -> ApiResponse[T]:
        """构建错误响应
        
        Args:
            code: 业务状态码， RespCodeEnum 枚举
            message: 提示信息，默认为 None，会使用响应码的默认提示信息
        
        Returns:
            ApiResponse 对象
        """
        resp_code = code
        
        return ApiResponse[T](
            code=resp_code,
            message=message or resp_code.msg,
            data=None,
            timestamp=int(datetime.now().timestamp() * 1000)
        )
    
    @classmethod
    def pagination(cls, records: List[T], total: int, page_num: int, page_size: int) -> PaginationResponse[T]:
        """构建分页响应
        
        Args:
            records: 当前页数据列表
            total: 总条数
            page_num: 当前页码
            page_size: 每页条数
        
        Returns:
            PaginationResponse 对象
        """
        # 计算总页数
        pages = (total + page_size - 1) // page_size if page_size > 0 else 0
        
        pagination_data = PaginationData[T](
            records=records,
            total=total,
            page=page_num,
            size=page_size,
            pages=pages
        )
        
        return PaginationResponse[T](
            code=RespCodeEnum.SUCCESS,
            message=RespCodeEnum.SUCCESS.msg,
            data=pagination_data,
            timestamp=int(datetime.now().timestamp() * 1000)
        )
