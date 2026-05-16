from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import BaseModel
from sqlalchemy import JSON


class OperLog(BaseModel):
    """操作日志模型"""

    __tablename__ = "sys_oper_log"
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

    # -------------------------- 请求参数字段 --------------------------
    path_params: Mapped[dict | None] = mapped_column(
        JSON(none_as_null=True),
        default=None,
        nullable=True,
        comment="路径参数（如/api/user/{id}中的id）"
    )
    query_params: Mapped[dict | None] = mapped_column(
        JSON(none_as_null=True),
        default=None,
        nullable=True,
        comment="查询参数（如/api/user?name=test中的name）"
    )
    request_body: Mapped[dict | None] = mapped_column(
        JSON(none_as_null=True),
        default=None,
        nullable=True,
        comment="POST/PUT请求体数据"
    )
