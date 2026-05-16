from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict
from typing import Any, Dict


class OperLogCreateRequest(BaseModel):
    """操作日志创建请求"""

    trace_id: str = Field(..., description="分布式链路追踪ID", max_length=64)
    request_method: str = Field(..., description="HTTP请求方法", max_length=16)
    api_path: str = Field(..., description="API接口路径", max_length=255)
    api_name: str | None = Field(None, description="API接口名称", max_length=128)
    module: str | None = Field(None, description="所属业务模块", max_length=64)
    operator_id: str | None = Field(None, description="操作员ID", max_length=64)
    client_ip: str = Field(..., description="客户端IP（兼容IPv6）", max_length=46)
    ip_country: str | None = Field(None, description="国家", max_length=32)
    ip_province: str | None = Field(None, description="省份/直辖市", max_length=32)
    ip_city: str | None = Field(None, description="城市", max_length=32)
    response_code: str | None = Field(None, description="响应码", max_length=32)
    response_msg: str | None = Field(None, description="响应信息/错误描述", max_length=512)
    response_data: dict | None = Field(None, description="响应数据")
    cost_time: int = Field(..., description="请求耗时（毫秒）", ge=0)
    path_params: dict | None = Field(None, description="路径参数（如/api/user/{id}中的{id）")
    query_params: dict | None = Field(None, description="查询参数（如/api/user?name=test中的name）")
    request_body: dict | list | None = Field(None, description="POST/PUT请求体数据")


class OperLogListQueryRequest(BaseModel):
    """操作日志列表查询请求"""

    page_num: int = Field(1, description="当前页码", ge=1, example=1)
    page_size: int = Field(10, description="每页条数", ge=1, le=100, example=100)
    trace_id: str | None = Field(None, description="分布式链路追踪ID", max_length=64)
    request_method: str | None = Field(None, description="HTTP请求方法", max_length=16)
    api_path: str | None = Field(None, description="API接口路径（模糊查询）", max_length=255)
    api_name: str | None = Field(None, description="API接口名称（模糊查询）", max_length=128)
    module: str | None = Field(None, description="所属业务模块", max_length=64)
    operator_id: str | None = Field(None, description="操作员ID", max_length=64)
    client_ip: str | None = Field(None, description="客户端IP（模糊查询）", max_length=46)
    response_code: str | None = Field(None, description="响应码", max_length=32)
    start_time: datetime | None = Field(None, description="开始时间")
    end_time: datetime | None = Field(None, description="结束时间")


class OperLogResponse(BaseModel):
    """操作日志响应"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="日志ID")
    trace_id: str = Field(..., description="分布式链路追踪ID")
    request_method: str = Field(..., description="HTTP请求方法")
    api_path: str = Field(..., description="API接口路径")
    api_name: str | None = Field(None, description="API接口名称")
    module: str | None = Field(None, description="所属业务模块")
    operator_id: str | None = Field(None, description="操作员ID")
    client_ip: str = Field(..., description="客户端IP（兼容IPv6）")
    ip_country: str | None = Field(None, description="国家")
    ip_province: str | None = Field(None, description="省份/直辖市")
    ip_city: str | None = Field(None, description="城市")
    ip_location: str | None = Field(None, description="IP归属地")
    response_code: str | None = Field(None, description="响应码")
    response_msg: str | None = Field(None, description="响应信息/错误描述")
    response_data: dict | list | None = Field(None, description="响应数据/完整响应内容")
    cost_time: int = Field(..., description="请求耗时（毫秒）")
    create_time: datetime = Field(..., description="创建时间")