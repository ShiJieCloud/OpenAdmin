from app.models.base import BaseModel, BaseRelation
from app.models.user import User
from app.models.role import Role
from app.models.dept import Dept
from app.models.post import Post
from app.models.permission import Permission
from app.models.user_post import UserPost
from app.models.post_role import PostRole
from app.models.user_role import UserRole
from app.models.role_permission import RolePermission

__all__ = [
    "BaseModel",
    "BaseRelation",
    "User",
    "Role",
    "Dept",
    "Post",
    "Permission",
    "UserPost",
    "PostRole",
    "UserRole",
    "RolePermission",
]
