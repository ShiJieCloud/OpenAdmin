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

    trace_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        comment="链路追踪ID"
    )
    user_id: Mapped[int | None] = mapped_column(
        BigInteger,
        nullable=True,
        comment="用户ID"
    )
    username: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="用户名称"
    )
    response_code: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="响应码"
    )
    response_msg: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="响应信息/错误描述"
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
    os: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True,
        comment="操作系统"
    )
    browser: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="浏览器"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="客户端标识"
    )
