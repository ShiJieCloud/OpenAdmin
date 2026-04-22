from enum import Enum


class RespCodeEnum(Enum):
    """响应码枚举类
    
    用于定义系统中所有的响应码，每个枚举成员包含业务码和提示信息
    
    格式：枚举成员 = (响应码, 提示信息)
    
    特性：
    1. print(RespCodeEnum.SUCCESS) → 输出 000000
    2. RespCodeEnum.SUCCESS.code → 000000
    3. RespCodeEnum.SUCCESS.msg → 请求成功
    """

    # 成功
    SUCCESS = ("000000", "请求成功")
    
    # 客户端错误
    BAD_REQUEST = ("400", "请求参数错误")
    UNAUTHORIZED = ("401", "未授权")
    FORBIDDEN = ("403", "禁止访问")
    NOT_FOUND = ("404", "资源不存在")
    METHOD_NOT_ALLOWED = ("405", "方法不允许")
    CONFLICT = ("409", "资源冲突")
    
    # 服务器错误
    INTERNAL_SERVER_ERROR = ("500", "服务器内部错误")
    SERVICE_UNAVAILABLE = ("503", "服务不可用")
    
    # 业务错误
    VALIDATION_ERROR = ("422", "数据验证错误")
    AUTHENTICATION_ERROR = ("401", "认证失败")
    PERMISSION_ERROR = ("403", "权限不足")
    RESOURCE_ERROR = ("404", "资源错误")
    
    def __init__(self, code, msg):
        self.code = code
        self.msg = msg
    
    def __str__(self):
        return self.code
