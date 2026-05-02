from enum import Enum


class RespCodeEnum(Enum):
    """
    系统全局响应码枚举类

    编码规则（固定7位）：
      - 第1位：一级分类（0=成功 / T=技术错误 / B=业务错误 / E=第三方错误）
      - 第2-3位：二级分类（2位字母，详见类内注释）
      - 第4-7位：4位数字序号（0000~9999）

    完整格式：XXXNNNN（共7位）
      - 示例：0000000 = 成功
      - 示例：BPW0001 = 业务类-密码错误-序号0001
    """

    # ==================== 0：成功 ====================
    SUCCESS = ("0000000", "请求成功")

    # ==================== T：技术类错误（Technical Error） ====================
    INTERNAL_SERVER_ERROR = ("TSV0001", "服务器内部异常")

    # ==================== B：业务类错误（Business Error） ====================
    # B-AU = 认证授权 (Auth)
    TOKEN_INVALID = ("BAU0001", "Token 无效")
    TOKEN_EXPIRED = ("BAU0002", "Token 已过期")
    TOKEN_TYPE_ERROR = ("BAU0003", "Token 类型错误")
    LOGIN_EXPIRED = ("BAU0004", "登录已失效，请重新登录")
    PERM_DENIED = ("BAU0005", "权限不足，无法访问该资源")

    # B-US = 用户相关 (User)
    USER_NOT_EXIST = ("BUS0001", "用户不存在")
    ACCOUNT_STATUS_ABNORMAL = ("BUS0002", "账号状态异常，请联系管理员")

    # B-PW = 密码认证 (Password)
    PWD_VERIFY_FAIL = ("BPW0001", "用户名或密码错误，，剩余尝试次数: {count} 次")
    ACCOUNT_LOCKED = ("BPW0002", "账号已被锁定，请稍后再试或联系管理员")
    
    # B-GE = 通用业务 (General)
    PARAM_INVALID = ("BGE0001", "参数无效")
    QUERY_CONDITION_INVALID = ("BGE0002", "查询条件不能为空")

    # ==================== E：第三方错误（Third-party Error） ====================


    def __init__(self, code: str, msg: str):
        self.code = code
        self.msg = msg
