from sqlalchemy import BigInteger, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseRelation


class UserPost(BaseRelation):
    """用户-岗位关联模型"""

    __tablename__ = "sys_user_post"
    __table_args__ = (
        UniqueConstraint("user_id", "post_id", name="uk_user_post"),
        {"comment": "用户-岗位关联表"},
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="用户ID"
    )
    post_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="岗位ID"
    )
