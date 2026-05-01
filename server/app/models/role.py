from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT


from app.models.base import BaseModel


class Role(BaseModel):
    """角色模型"""
    __tablename__ = "sys_role"
    
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
    role_sort: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="角色排序"
    )
    description: Mapped[str] = mapped_column(
        String(255),
        default=None,
        nullable=True,
        comment="角色描述"
    )
    status: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="状态 0=启用 1=禁用"
    )
