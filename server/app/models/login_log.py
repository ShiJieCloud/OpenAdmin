from sqlalchemy import String, BigInteger, DateTime, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.mysql import TINYINT

from app.models.base import BaseModel
from datetime import datetime


class LoginLog(BaseModel):
    """登录日志模型"""

    __tablename__ = "sys_login_log"
    __table_args__ = (
        {"comment": "系统用户登录日志表"},
    )

    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="登录账号"
    )
    login_type: Mapped[int | None] = mapped_column(
        TINYINT,
        nullable=True,
        comment="登录类型 1-账号密码 2-短信 3-第三方 4-扫码 5-单点（登出时为NULL）"
    )
    operate_type: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        comment="操作类型 1-登录 2-登出"
    )
    operate_status: Mapped[int] = mapped_column(
        TINYINT,
        nullable=False,
        comment="状态 0-失败 1-成功"
    )
    fail_reason: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
        comment="失败原因"
    )
    client_ip: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="客户端IP"
    )
    ip_country: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="国家"
    )
    ip_province: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="省份/直辖市"
    )
    ip_city: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="城市"
    )
    ip_location: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="完整属地：国家-省-市"
    )
    device_type: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="设备类型"
    )
    browser: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="浏览器"
    )
    trace_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="链路追踪ID"
    )
    operate_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        comment="操作时间"
    )
