from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT
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
    perm_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="权限名称"
    )
    perm_code: Mapped[str] = mapped_column(
        String(128),
        nullable=False,
        unique=True,
        comment="权限标识"
    )
    perm_type: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="权限类型：0=按钮 1=接口"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="排序"
    )
