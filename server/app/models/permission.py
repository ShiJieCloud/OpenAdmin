from sqlalchemy import String, BigInteger, Integer, Enum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT
from app.core.enums import PermTypeEnum
from app.models.base import BaseModel


class Permission(BaseModel):
    """权限模型"""

    __tablename__ = "sys_permission"
    __table_args__ = (
        {"comment": "权限表"},
    )

    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        comment="父菜单ID"
    )
    perm_type: Mapped[PermTypeEnum] = mapped_column(
        String(20),
        nullable=False,
        default=PermTypeEnum.MENU,
        index=True,
        comment="权限类型：menu=菜单 button=按钮"
    )
    perm_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
        comment="权限标识"
    )
    perm_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="名称"
    )
    path: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="路由地址"
    )
    component: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="前端组件"
    )
    icon: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="菜单图标"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=999,
        comment="显示顺序"
    )
    status: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="状态 0=启用 1=禁用"
    )
