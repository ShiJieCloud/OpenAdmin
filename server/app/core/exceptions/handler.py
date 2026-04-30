from app.core.enums import RespCodeEnum
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.exceptions import BusinessError
from app.core.response import ResponseBuilder


def register_exception_handlers(app: FastAPI):
    """注册全局异常处理器
    
    Args:
        app: FastAPI 应用实例
    """
    
    @app.exception_handler(BusinessError)
    async def business_error_handler(request: Request, exc: BusinessError):
        """业务错误异常处理器
        
        Args:
            request: 请求对象
            exc: 业务错误异常实例
        
        Returns:
            JSONResponse: 统一格式的错误响应
        """
        response = ResponseBuilder.error(code=exc.code, message=exc.message)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump()
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(request: Request, exc: RequestValidationError):
        """请求参数验证错误处理器
        
        Args:
            request: 请求对象
            exc: 请求参数验证错误实例
        
        Returns:
            JSONResponse: 统一格式的错误响应
        """
        # 提取验证错误信息
        error_details = []
        for error in exc.errors():
            field = ".".join([str(loc) for loc in error.get("loc", [])])
            msg = error.get("msg", "参数验证错误")
            error_details.append(f"{field}: {msg}")
        
        error_message = "; ".join(error_details)
        response = ResponseBuilder.error(code="400", message=error_message)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump()
        )
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """全局异常处理器
        
        Args:
            request: 请求对象
            exc: 异常实例
        
        Returns:
            JSONResponse: 统一格式的错误响应
        """
        # 记录异常信息
        print(f"全局异常捕获: {exc}")
        
        # 返回统一格式的错误响应
        response = ResponseBuilder.error(RespCodeEnum.INTERNAL_SERVER_ERROR)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=response.model_dump()
        )
