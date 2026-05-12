from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel


class OperateLog(BaseModel):
    """操作日志模型"""

    __tablename__ = "sys_operate_log"
    __table_args__ = (
        {"comment": "系统操作日志表"},
    )

    trace_id: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
        index=True,
        comment="分布式链路追踪ID"
    )
    request_method: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        comment="HTTP请求方法"
    )
    api_path: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        index=True,
        comment="API接口路径"
    )
    api_name: Mapped[str | None] = mapped_column(
        String(128),
        nullable=True,
        comment="API接口名称"
    )
    module: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="所属业务模块"
    )
    operator_id: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
        comment="操作员ID"
    )
    client_ip: Mapped[str] = mapped_column(
        String(46),
        nullable=False,
        comment="客户端IP（兼容IPv6）"
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
    cost_time: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="请求耗时（毫秒）"
    )
    user_agent: Mapped[str | None] = mapped_column(
        String(512),
        nullable=True,
        comment="客户端标识"
    )
    terminal_type: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
        comment="终端类型"
    )
