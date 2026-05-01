from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseRelation


class RolePermission(BaseRelation):
    """角色-权限关联模型"""

    __tablename__ = "sys_role_permission"
    __table_args__ = (
        UniqueConstraint("role_id", "perm_id", name="uk_role_perm"),
        {"comment": "角色-权限关联表"},
    )

    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="角色ID"
    )
    perm_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="权限ID"
    )
        