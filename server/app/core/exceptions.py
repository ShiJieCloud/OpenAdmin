from typing import Optional
from app.core.enums import RespCodeEnum


class BusinessError(Exception):
    """业务错误异常
    
    用于处理业务逻辑相关的错误
    """
    
    def __init__(self, code: Optional[RespCodeEnum] = None, message: Optional[str] = None):
        """
        Args:
            code: 响应码枚举，默认为 None，使用默认业务错误响应码
            message: 错误提示信息，默认为 None，使用响应码的默认提示信息
        """
        self.code = code
        self.message = message or self.code.msg
        super().__init__(self.message)