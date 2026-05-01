from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT
from app.models.base import BaseModel


class Dept(BaseModel):
    """部门模型"""

    __tablename__ = "sys_dept"
    __table_args__ = (
        {"comment": "部门表"},
    )
    
    parent_id: Mapped[int] = mapped_column(
        BigInteger,
        default=0,
        nullable=False,
        index=True,
        comment="上级部门ID（0=顶级）"
    )
    dept_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="部门名称"
    )
    sort: Mapped[int] = mapped_column(
        Integer,
        default=999,
        comment="显示顺序（越小越靠前）"
    )
    status: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="状态 0=启用 1=禁用"
    )
