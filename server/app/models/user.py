from sqlalchemy import Boolean, String, BigInteger, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT


from app.models.base import BaseModel


class User(BaseModel):
    """用户模型"""

    __tablename__ = "sys_user"
    __table_args__ = (
        {"comment": "用户表"},
    )
    
    username: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        comment="登录账号（唯一）"
    )
    employee_no: Mapped[str | None] = mapped_column(
        String(12),
        nullable=True,
        unique=True,
        index=True,
        comment="工号（唯一）"
    )
    password: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="登录密码（加密存储）"
    )
    nickname: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="用户昵称/姓名"
    )
    avatar: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="头像URL"
    )
    email: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
        comment="邮箱"
    )
    phone: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="手机号"
    )
    sex: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        comment="性别：0=未知 1=男 2=女"
    )
    status: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        nullable=False,
        comment="账号状态：0=正常 1=禁用 2=锁定 3=注销 4=冻结"
    )
    dept_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        index=True,
        comment="所属部门ID"
    )
    last_login_ip: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="最后登录IP"
    )
    last_login_date: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="最后登录时间"
    )
    login_fail_count: Mapped[int] = mapped_column(
        Integer,
        default=0,
        comment="连续登录失败次数"
    )
    lock_time: Mapped[DateTime | None] = mapped_column(
        DateTime,
        nullable=True,
        comment="账号锁定时间"
    )
    remark: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="备注"
    )
    del_flag: Mapped[int] = mapped_column(
        TINYINT,
        default=0,
        nullable=False,
        comment="删除标志：0=未删除 1=已删除"
    )
    is_superuser: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="是否超级管理员"
    )
