from sqlalchemy import String, BigInteger, SMALLINT, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class UserApply(BaseModel):
    """用户注册申请模型"""

    __tablename__ = "sys_user_apply"
    __table_args__ = (
        {"comment": "用户注册申请表"},
    )

    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="申请登录账号"
    )
    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="登录密码（加密存储）"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=False,
        comment="手机号"
    )
    status: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        nullable=False,
        comment="审核状态：0=待审核 1=已通过 2=已拒绝 3=撤销"
    )
    audit_user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="审批管理员ID"
    )
    audit_time: Mapped[DateTime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="审批时间"
    )
    audit_reason: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="拒绝原因"
    )
    del_flag: Mapped[int] = mapped_column(
        SMALLINT,
        default=0,
        nullable=False,
        comment="删除标志：0=正常 1=删除"
    )
