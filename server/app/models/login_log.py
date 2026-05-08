from sqlalchemy import String, BigInteger, DateTime, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT

from app.models.base import BaseModel
from datetime import datetime


class LoginLog(BaseModel):
    """登录日志模型"""

    __tablename__ = "sys_login_log"
    __table_args__ = (
        {"comment": "系统登录日志表"},
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
        index=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="登录账号（手机号/邮箱/用户名）"
    )
    operate_type: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        comment="操作类型：1-登录 2-登出"
    )
    login_type: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        default=1,
        comment="登录类型：1-账号密码 2-短信 3-第三方 4-扫码 5-邮箱"
    )
    login_status: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        default=0,
        comment="状态：0-成功 1-失败"
    )
    fail_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="失败原因"
    )
    login_ip: Mapped[str] = mapped_column(
        String(45),
        nullable=False,
        comment="IP地址"
    )
    login_location: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="登录地点"
    )
    device_type: Mapped[int | None] = mapped_column(
        TINYINT,
        default=0,
        comment="设备：0-未知 1-PC 2-移动端 3-平板"
    )
    os_name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="操作系统"
    )
    browser_name: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="浏览器"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="UA信息"
    )
    operate_time: Mapped[datetime] = mapped_column(
        default=datetime.now(),
        nullable=False,
        comment="操作时间（登录/登出时间）"
    )
    remark: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
        comment="备注"
    )