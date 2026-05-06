from app.crud.base import BaseCRUD
from app.crud.user import UserCRUD
from app.crud.permission import PermissionCRUD
from app.crud.role import RoleCRUD
from app.crud.post import PostCRUD

__all__ = [
    "BaseCRUD",
    "UserCRUD",
    "PermissionCRUD",
    "RoleCRUD",
    "PostCRUD"
]
