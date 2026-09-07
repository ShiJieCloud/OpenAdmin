from sqlalchemy import String, Integer, SMALLINT
from sqlalchemy.orm import Mapped, mapped_column


from app.models.base import BaseModel


class Role(BaseModel):
    """角色模型"""

    __tablename__ = "sys_role"
    __table_args__ = (
        {"comment": "角色表"},
    )
    
    role_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="角色名称"
    )
    role_code: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
        comment="角色唯一编码"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="显示顺序（越小越靠前）"
    )
    description: Mapped[str] = mapped_column(
        String(255),
        default=None,
        nullable=True,
        comment="角色描述"
    )
    status: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        comment="状态 0=启用 1=禁用"
    )
