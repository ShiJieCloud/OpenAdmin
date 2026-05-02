from app.core.exceptions.business import BusinessError


class PermDeniedException(BusinessError):
    """权限拒绝异常"""
    pass
