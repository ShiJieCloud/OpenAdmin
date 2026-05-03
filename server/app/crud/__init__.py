from app.crud.base import BaseCRUD
from app.crud.user import UserCRUD
from app.crud.permission import PermissionCRUD
from app.crud.role import RoleCRUD

__all__ = [
    "BaseCRUD",
    "UserCRUD",
    "PermissionCRUD",
    "RoleCRUD"
]
