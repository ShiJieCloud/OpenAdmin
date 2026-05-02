from enum import StrEnum


class UserPermEnum(StrEnum):
    """用户模块权限码"""
    READ = "user:read"
    CREATE = "user:create"
    UPDATE = "user:update"
    DELETE = "user:delete"
    EXPORT = "user:export"
    IMPORT = "user:import"
    RESET_PASSWORD = "user:reset_password"


class RolePermEnum(StrEnum):
    """角色模块权限码"""
    READ = "role:read"
    CREATE = "role:create"
    UPDATE = "role:update"
    DELETE = "role:delete"


class PermPermEnum(StrEnum):
    """权限模块权限码"""
    READ = "perm:read"
    CREATE = "perm:create"
    UPDATE = "perm:update"
    DELETE = "perm:delete"


class DeptPermEnum(StrEnum):
    """部门模块权限码"""
    READ = "dept:read"
    CREATE = "dept:create"
    UPDATE = "dept:update"
    DELETE = "dept:delete"


class PostPermEnum(StrEnum):
    """岗位模块权限码"""
    READ = "post:read"
    CREATE = "post:create"
    UPDATE = "post:update"
    DELETE = "post:delete"


class MenuPermEnum(StrEnum):
    """菜单模块权限码"""
    READ = "menu:read"
    CREATE = "menu:create"
    UPDATE = "menu:update"
    DELETE = "menu:delete"


class LogPermEnum(StrEnum):
    """日志模块权限码"""
    READ = "log:read"
    EXPORT = "log:export"
    DELETE = "log:delete"


class SystemPermEnum(StrEnum):
    """系统模块权限码"""
    SETTING_VIEW = "system:setting_view"
    SETTING_UPDATE = "system:setting_update"
    CACHE_CLEAR = "system:cache_clear"


# 统一总出口
class PermEnum:
    User = UserPermEnum
    Role = RolePermEnum
    Perm = PermPermEnum
    Dept = DeptPermEnum
    Post = PostPermEnum
    Menu = MenuPermEnum
    Log = LogPermEnum
    System = SystemPermEnum
