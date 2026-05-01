from app.core.enums import RespCodeEnum


class BusinessError(Exception):
    """业务错误异常
    
    用于处理业务逻辑相关的错误
    """
    
    def __init__(self, resp_code: RespCodeEnum):
        """
        Args:
            resp_code: 响应码枚举
        """
        self.code = resp_code.code
        self.message = resp_code.msg
        super().__init__(self.message)