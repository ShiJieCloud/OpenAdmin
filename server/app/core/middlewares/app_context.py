import time
import uuid
from typing import Any

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import app_config
from app.core.context import AppContext
from app.core.database import get_async_db_session
from app.core.logger import logger

from app.schemas import LoginLogCreateRequest, OperLogCreateRequest
from app.schemas.common import IPLocationInfo, UserAgentInfo
from app.services import LoginLogService, OperLogService
from app.utils import HttpUtils

LOGIN_PATH = "/login/"
AUTH_PREFIX = "/auth"

class AppContextMiddleware(BaseHTTPMiddleware):
    """
    上下文中间件：为每个请求提供独立上下文环境，并自动记录操作/登录日志

    核心能力：
    1. 初始化请求上下文（TraceID、客户端IP、请求信息等）
    2. 收集请求/响应全量数据
    3. 区分接口类型记录专属日志（登录日志/操作日志）
    4. 请求结束自动清理上下文，避免内存泄漏
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        中间件核心调度方法（主流程）

        步骤拆分：初始化 → 过滤非API请求 → 处理请求 → 收集数据 → 记录日志 → 清理上下文
        """
        logger.info("开始处理请求")

        # 1. 初始化请求上下文（生成TraceID、记录客户端IP等基础信息）
        self._init_request_context(request)

        start_time = time.perf_counter()
        try:
            api_path = request.url.path

            # 2. 过滤非 API 接口请求（仅处理配置的 API 前缀路径）
            if not api_path.startswith(app_config.API_PREFIX):
                logger.debug(f"非 API 接口，跳过处理")
                return await call_next(request)

            # 3. 收集请求参数（查询参数，请求体参数）
            request_params = await HttpUtils.get_request_params(request)
            logger.debug(f"收集请求参数完成，params={request_params}")

            # 4. 执行核心请求处理，获取响应
            response: Response = await call_next(request)

            # 5. 过滤 GET 请求
            if request.method == "GET":
                return response

            # 6. 计算请求耗时（毫秒）
            cost_time = self._calculate_cost_time(start_time)
            
            # 7. 收集路径参数（路径参数由路由匹配后生成，必须在 call_next 之后获取）
            path_params = dict(request.path_params)
            if path_params and len(path_params) > 0:
                request_params["path_params"] = path_params
                logger.debug(f"收集路径参数完成，params={path_params}")
            
            # 8. 收集响应信息（状态码、消息、数据） 
            response_info = await self._collect_response_info(response)

            # 9. 收集 IP 归属地信息
            ip_location_info = HttpUtils.get_ip_location(AppContext.get_client_ip())
            logger.debug(f"收集 IP 归属地信息完成，ip_location_info={ip_location_info.model_dump()}")

            # 10. 记录日志（登录日志/操作日志）
            if LOGIN_PATH in api_path:
                # 登录接口 → 记录登录日志
                logger.debug(f"登录接口，记录登录日志")
                user_agent_info = HttpUtils.get_user_agent_info(request)
                await self._record_login_log(response_info, user_agent_info, ip_location_info)
            elif AUTH_PREFIX not in api_path:
                # 非 auth 接口 → 记录操作日志
                logger.debug(f"业务接口，记录操作日志")
                api_metadata = self._get_api_metadata(request)
                await self._record_oper_log(api_metadata, ip_location_info, cost_time, request_params, response_info)

            logger.info(f"请求处理完成，耗时: {cost_time}ms")
            return response
        finally:
            AppContext.clear()

    def _init_request_context(self, request: Request):
        """初始化请求上下文"""
        AppContext.set_trace_id(str(uuid.uuid4()).replace("-", ""))
        AppContext.set_client_ip(HttpUtils.get_client_ip(request))
        AppContext.set_request_method(request.method)
        AppContext.set_request_path(request.url.path)
        logger.info("请求上下文初始化完成")

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

        response_info = {
            "response_code": response_code,
            "response_msg": response_msg,
            "response_data": response_data,
        }
        logger.debug(f"接口返回结果，response_info={response_info}")
        return response_info

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
            logger.error(f"获取API元数据失败: {e}")

        api_metadata = {
            "request_method": request_method,
            "api_path": api_path,
            "api_name": api_name,
            "module": module
        }
        logger.debug(f"获取API元数据完成，api_metadata={api_metadata}")
        return api_metadata

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
                logger.info("登录日志记录成功")
        except Exception as e:
            logger.exception(f"登录日志记录失败: {e}")

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
                logger.info("操作日志记录成功")
        except Exception as e:
            logger.exception(f"操作日志记录失败: {e}")

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
    logger.info("正在注册 [AppContextMiddleware] 上下文中间件")
    app.add_middleware(AppContextMiddleware)
    logger.info("[AppContextMiddleware] 上下文中间件注册完成")
