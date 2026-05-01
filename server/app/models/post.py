from sqlalchemy import String, BigInteger, Integer
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT


from app.models.base import BaseModel


class Post(BaseModel):
    """岗位模型"""
    
    __tablename__ = "sys_post"
    __table_args__ = (
        {"comment": "岗位表"},
    )
    
    post_name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="岗位名称"
    )
    dept_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="所属部门ID（可为空）"
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
    remark: Mapped[str] = mapped_column(
        String(255),
        default="",
        comment="备注"
    )
