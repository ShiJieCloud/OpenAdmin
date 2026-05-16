import uuid
from datetime import datetime
from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.context import AppContext
import time
from app.services import OperLogService, LoginLogService
from app.schemas import OperLogCreateRequest, LoginLogCreateRequest
from app.core.database import get_async_db_session
from app.utils import HttpUtils
from app.schemas.common import IPLocationInfo, UserAgentInfo

AUTH_PATH = "/auth/login"

class ContextMiddleware(BaseHTTPMiddleware):
    """
    上下文中间件
    为每个请求自动初始化、填充和清理 AppContext 上下文数据
    
    功能特性：
    - 自动生成并注入唯一请求ID，支持链路追踪
    - 自动记录请求路径、请求方法、客户端IP等基础信息
    - 请求结束后自动清理上下文，避免内存泄漏和数据污染
    - 支持将请求ID注入响应头，便于前端排查问题
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        try:

            # 设置请求ID
            AppContext.set_trace_id(str(uuid.uuid4()))

            start_time = time.perf_counter()

            response: Response = await call_next(request)

            # 记录请求路径、请求方法、客户端IP等基础信息
            request_method = request.method
            api_path = request.url.path

            if '/api' not in api_path:
                return response

            # 5. 尝试获取接口名称（summary）- 接口执行完成后获取
            api_name = None
            try:
                # 【正确】从 scope 中获取，不是从属性获取
                route = request.get("route")
                if route and hasattr(route, "summary"):
                    api_name = route.summary

                # 获取tags信息
                tags = route.tags
                if tags:
                    module = tags[0]
                print(f"tags: {module}")
            except Exception as e:
                print(f"获取接口名称失败: {str(e)}")
            
           
            operator_id = AppContext.get_current_user_id()
            cost_time = time.perf_counter() - start_time
            
            client_ip = request.client.host
            ip_location_info: IPLocationInfo = HttpUtils.get_ip_location(client_ip)

            user_agent_info: UserAgentInfo = HttpUtils.get_user_agent_info(request)

            if AUTH_PATH in api_path:
                # 记录登陆日志
                await self._record_login_log(
                    ip_location_info=ip_location_info,
                    user_agent_info=user_agent_info
                )

            else:
                # 记录操作日志
                await self._record_oper_log(
                cost_time=cost_time,
                api_name=api_name,
                module=module,
                request_method=request_method,
                api_path=api_path,
                ip_location_info=ip_location_info,
                user_agent_info=user_agent_info,
            )

            return response
        finally:
            AppContext.clear()

    async def _record_oper_log(
        self, 
        cost_time: float, 
        api_name: str, 
        module: str, 
        request_method: str, 
        api_path: str, 
        ip_location_info: IPLocationInfo,
        user_agent_info: UserAgentInfo,
    ):
        """记录操作日志"""
        try:
            async with get_async_db_session() as db_session:
                service = OperLogService(db_session)

                oper_log_data = OperLogCreateRequest(
                    trace_id=AppContext.get_trace_id(),
                    cost_time=int(cost_time * 1000),
                    operator_id=AppContext.get_current_user_id(),
                    api_name=api_name,
                    module=module,
                    request_method=request_method,
                    api_path=api_path,
                    client_ip=ip_location_info.ip,
                    ip_country=ip_location_info.country,
                    ip_province=ip_location_info.province,
                    ip_city=ip_location_info.city,
                    ip_location=ip_location_info.full_location,
                    terminal_type=user_agent_info.device_type,
                    user_agent=user_agent_info.user_agent
                )
                await service.create_oper_log(oper_log_data)
        except Exception as e:
            print(f"oper_log 日志插入失败: {str(e)}")

    async def _record_login_log(self, ip_location_info: IPLocationInfo, user_agent_info: UserAgentInfo):
        """记录登陆日志"""
        try:

            async with get_async_db_session() as db_session:
                log_service = LoginLogService(db_session)
                login_log_data = LoginLogCreateRequest(
                    user_id=AppContext.get_current_user_id(),
                    username=AppContext.get_current_username(),
                    login_type= 1,
                    operate_type= 1,
                    operate_status= 1,
                    fail_reason=None,
                    client_ip=ip_location_info.ip,
                    ip_country=ip_location_info.country,
                    ip_province=ip_location_info.province,
                    ip_city=ip_location_info.city,
                    ip_location=ip_location_info.full_location,
                    device_type=user_agent_info.device_type,
                    trace_id=AppContext.get_trace_id(),
                )
                await log_service.create_login_log(login_log_data)
        except Exception as e:
            print(f"login_log 日志插入失败: {str(e)}")



def setup_context_middleware(app: FastAPI):
    """配置上下文中间件
    
    为 FastAPI 应用实例添加上下文中间件，确保每个请求
    都能获得独立、安全的上下文环境
    
    Args:
        app: FastAPI 应用实例
    """
    app.add_middleware(ContextMiddleware)
