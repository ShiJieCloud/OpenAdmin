from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT
from app.models.base import BaseModel


class Menu(BaseModel):
    """菜单模型"""

    __tablename__ = "sys_menu"
    __table_args__ = (
        {"comment": "菜单表(目录+页面)"},
    )

    menu_name: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="菜单名称"
    )
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        comment="父菜单ID"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="排序"
    )
    path: Mapped[str] = mapped_column(
        String(255),
        default="",
        comment="前端路由地址"
    )
    component: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="前端组件路径"
    )
    menu_type: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        comment="菜单类型：0=目录 1=页面"
    )
    icon: Mapped[str] = mapped_column(
        String(128),
        default="",
        comment="菜单图标"
    )
    is_hidden: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="是否隐藏：0=显示 1=隐藏"
    )
    is_frame: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="是否内嵌：0=否 1=是"
    )
    is_external: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="是否外部链接：0=否 1=是"
    )

