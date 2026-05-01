from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseRelation


class PostRole(BaseRelation):
    """岗位-角色关联模型"""

    __tablename__ = "sys_post_role"
    __table_args__ = (
        UniqueConstraint("post_id", "role_id", name="uk_post_role"),
        {"comment": "岗位-角色关联表"},
    )

    post_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="岗位ID"
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="角色ID"
    )