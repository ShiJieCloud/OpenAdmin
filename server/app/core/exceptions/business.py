from app.core.enums import RespCodeEnum


class BusinessError(Exception):
    """业务错误异常
    
    用于处理业务逻辑相关的错误
    """
    
    def __init__(self, resp_code: RespCodeEnum, **kwargs):
        """
        Args:
            resp_code: 响应码枚举
            **kwargs: 动态参数，用于格式化消息模板
        """
        self.code = resp_code.code
        # 支持动态消息格式化，如 "剩余 {count} 次"
        self.message = resp_code.msg.format(**kwargs) if kwargs else resp_code.msg
        super().__init__(self.message)