from enum import StrEnum

class BasePermEnum(StrEnum):
    """
    基础权限码
    
    格式：模块:子模块:操作
    """
    __repr__ = lambda self: self.value


class UserPermEnum(BasePermEnum):
    """
    用户模块权限码
    """
    VIEW = "system:user:view"
    CREATE = "system:user:create"
    UPDATE = "system:user:update"
    DELETE = "system:user:delete"
    EXPORT = "system:user:export"
    IMPORT = "system:user:import"
    RESET_PASSWORD = "system:user:reset_password"


class RolePermEnum(BasePermEnum):
    """
    角色模块权限码
    """
    READ = "system:role:read"
    LIST = "system:role:list"
    CREATE = "system:role:create"
    UPDATE = "system:role:update"
    DELETE = "system:role:delete"


class PermPermEnum(BasePermEnum):
    """
    权限模块权限码
    """
    READ = "system:perm:read"
    CREATE = "system:perm:create"
    UPDATE = "system:perm:update"
    DELETE = "system:perm:delete"


class DeptPermEnum(BasePermEnum):
    """
    部门模块权限码
    """
    READ = "system:dept:read"
    CREATE = "system:dept:create"
    UPDATE = "system:dept:update"
    DELETE = "system:dept:delete"


class PostPermEnum(BasePermEnum):
    """
    岗位模块权限码
    """
    READ = "system:post:read"
    CREATE = "system:post:create"
    UPDATE = "system:post:update"
    DELETE = "system:post:delete"


class MenuPermEnum(BasePermEnum):
    """
    菜单模块权限码
    """
    READ = "system:menu:read"
    CREATE = "system:menu:create"
    UPDATE = "system:menu:update"
    DELETE = "system:menu:delete"


class LogPermEnum(BasePermEnum):
    """
    日志模块权限码
    """
    READ = "system:log:read"
    EXPORT = "system:log:export"
    DELETE = "system:log:delete"


class SystemPermEnum(BasePermEnum):
    """
    系统模块权限码
    """
    SETTING_VIEW = "system:setting:view"
    SETTING_UPDATE = "system:setting:update"
    CACHE_CLEAR = "system:cache:clear"


# 统一总出口
class PermCode:
    User = UserPermEnum
    Role = RolePermEnum
    Perm = PermPermEnum
    Dept = DeptPermEnum
    Post = PostPermEnum
    Menu = MenuPermEnum
    Log = LogPermEnum
    System = SystemPermEnum
