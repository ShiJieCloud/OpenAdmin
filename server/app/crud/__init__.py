from app.crud.base import BaseCRUD
from app.crud.user import UserCRUD
from app.crud.permission import PermissionCRUD
from app.crud.role import RoleCRUD
from app.crud.post import PostCRUD
from app.crud.menu import MenuCRUD

__all__ = [
    "BaseCRUD",
    "UserCRUD",
    "PermissionCRUD",
    "RoleCRUD",
    "PostCRUD",
    "MenuCRUD"
]
