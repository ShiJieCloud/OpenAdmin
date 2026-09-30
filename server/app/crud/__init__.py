from app.crud.base import BaseCRUD
from app.crud.user import UserCRUD
from app.crud.user_apply import UserApplyCRUD
from app.crud.permission import PermissionCRUD
from app.crud.role import RoleCRUD
from app.crud.post import PostCRUD
from app.crud.menu import MenuCRUD
from app.crud.dept import DeptCRUD
from app.crud.login_log import LoginLogCRUD
from app.crud.oper_log import OperLogCRUD

__all__ = [
    "BaseCRUD",
    "UserCRUD",
    "UserApplyCRUD",
    "PermissionCRUD",
    "RoleCRUD",
    "PostCRUD",
    "MenuCRUD",
    "DeptCRUD",
    "LoginLogCRUD",
    "OperLogCRUD",
]
