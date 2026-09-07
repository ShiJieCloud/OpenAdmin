from sqlalchemy import String, BigInteger, Integer, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import BaseModel


class Permission(BaseModel):
    """权限模型"""

    __tablename__ = "sys_permission"
    __table_args__ = (
        {"comment": "权限表"},
    )

    menu_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        comment="所属菜单ID"
    )
    name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="权限名称"
    )
    code: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        comment="权限标识"
    )
    description: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="权限描述"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="排序"
    )
    status: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        comment="状态：0=正常 1=停用"
    )
