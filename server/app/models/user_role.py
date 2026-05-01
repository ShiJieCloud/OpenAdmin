from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseRelation


class UserRole(BaseRelation):
    """用户-角色关联模型"""

    __tablename__ = "sys_user_role"
    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uk_user_role"),
        {"comment": "用户-角色关联表"},
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="用户ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="角色ID"
    )
