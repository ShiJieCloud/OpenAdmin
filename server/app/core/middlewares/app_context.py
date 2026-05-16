import time
import uuid
from typing import Any

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import app_config
from app.core.context import AppContext
from app.core.database import get_async_db_session
from app.schemas import LoginLogCreateRequest, OperLogCreateRequest
from app.schemas.common import IPLocationInfo, UserAgentInfo
from app.services import LoginLogService, OperLogService
from app.utils import HttpUtils

LOGIN_PATH = "/login"
AUTH_PREFIX = "/auth"

class AppContextMiddleware(BaseHTTPMiddleware):
    """
    上下文中间件

    为每个请求自动初始化、填充和清理 AppContext 上下文数据

    功能特性：
    - 自动生成并注入唯一请求ID，支持链路追踪
    - 自动记录请求路径、请求方法、客户端IP等基础信息
    - 请求结束后自动清理上下文，避免内存泄漏和数据污染
    - 支持记录操作日志和登录日志
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        AppContext.set_trace_id(str(uuid.uuid4()))
        start_time = time.perf_counter()

        try:
            api_path = request.url.path

            # 非 API 接口 → 跳过处理
            if not api_path.startswith(app_config.API_PREFIX):
                return await call_next(request)

            # 收集请求参数（查询参数，请求体参数）
            request_params = await HttpUtils.get_request_params(request)

            response: Response = await call_next(request)

            # 计算请求耗时
            cost_time = self._calculate_cost_time(start_time)
            
            # 收集路径参数
            path_params = dict(request.path_params)
            if path_params and len(path_params) > 0:
                request_params["path_params"] = path_params
            
            # 收集响应信息（状态码、消息、数据）
            response_info = await self._collect_response_info(response)

            # 收集 IP 归属地信息
            ip_location_info = HttpUtils.get_ip_location(HttpUtils.get_client_ip(request))

            if LOGIN_PATH in api_path:
                # 登录接口 → 记录登录日志
                user_agent_info = HttpUtils.get_user_agent_info(request)
                await self._record_login_log(response_info, user_agent_info, ip_location_info)
            elif AUTH_PREFIX not in api_path:
                # 非 auth 接口 → 记录操作日志
                api_metadata = self._get_api_metadata(request)
                await self._record_oper_log(request_params, api_metadata, response_info, ip_location_info, cost_time)

            return response
        finally:
            AppContext.clear()

    async def _collect_response_info(self, response: Response) -> dict[str, Any]:
        """收集响应信息（状态码、消息、数据）"""
        response_code = None
        response_msg = None
        response_data = None

        response_body = await HttpUtils.get_response_body(response)
        if response_body:
            response_code = response_body.get("code")
            response_msg = response_body.get("message")
            response_data = response_body

        return {
            "response_code": response_code,
            "response_msg": response_msg,
            "response_data": response_data,
        }

    def _get_api_metadata(self, request: Request) -> dict[str, Any]:
        """获取 API 元数据（接口名称、模块）"""
        request_method = request.method
        api_path = request.url.path
        api_name = None
        module = None

        try:
            route = request.get("route")
            if route:
                api_name = getattr(route, "summary", None)
                tags = getattr(route, "tags", None)
                if tags:
                    module = tags[0]
        except Exception as e:
            print(f"获取API元数据失败: {e}")

        return {
            "request_method": request_method,
            "api_path": api_path,
            "api_name": api_name,
            "module": module
        }

    async def _record_login_log(
        self,
        response_info: dict[str, Any],
        user_agent_info: UserAgentInfo,
        ip_location_info: IPLocationInfo,
    ) -> None:
        """记录登录日志"""
        try:
            async with get_async_db_session() as db_session:
                service = LoginLogService(db_session)
                log_data = LoginLogCreateRequest(
                    trace_id=AppContext.get_trace_id(),
                    user_id=AppContext.get_current_user_id(),
                    username=AppContext.get_current_username(),
                    **response_info,
                    **user_agent_info.model_dump(),
                    **ip_location_info.model_dump(),
                )
                await service.create_login_log(log_data)
        except Exception as e:
            print(f"登录日志记录失败: {e}")

    async def _record_oper_log(
        self,
        api_metadata: dict[str, Any],
        ip_location_info: IPLocationInfo,
        cost_time: int,
        response_info: dict[str, Any],
        request_params: dict[str, Any] | None,
    ) -> None:
        """记录操作日志"""
        try:
            async with get_async_db_session() as db_session:
                service = OperLogService(db_session)
                log_data = OperLogCreateRequest(
                    trace_id=AppContext.get_trace_id(),
                    operator_id=AppContext.get_current_user_id(),
                    **api_metadata,
                    **ip_location_info.model_dump(),
                    cost_time=cost_time,
                    **response_info,
                    **request_params,
                )
                await service.create_oper_log(log_data)
        except Exception as e:
            print(f"操作日志记录失败: {e}")

    def _calculate_cost_time(self, start_time: float) -> int:
        """计算请求耗时（毫秒）"""
        return int((time.perf_counter() - start_time) * 1000)


def setup_app_context_middleware(app: FastAPI) -> None:
    """
    配置上下文中间件

    为 FastAPI 应用实例添加上下文中间件，确保每个请求
    都能获得独立、安全的上下文环境

    Args:
        app: FastAPI 应用实例
    """
    app.add_middleware(AppContextMiddleware)
