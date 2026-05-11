from typing import Optional
from fastapi import Request
from user_agents import parse
from app.schemas.common import UserAgentInfo


class HttpUtils:
    """HTTP 请求工具类
    
    提供从 HTTP 请求中提取和解析信息的工具方法，
    包括获取客户端真实IP地址、解析User-Agent等功能。
    """
    
    @staticmethod
    def get_client_ip(request: Request) -> str:
        """获取客户端真实IP地址
        
        支持多种反向代理场景，按优先级从高到低尝试获取：
        1. X-Forwarded-For 头
        2. X-Real-IP 头
        3. 原生 request.client.address
        
        Args:
            request: FastAPI 请求对象
        
        Returns:
            客户端IP地址字符串
        """
        forwarded_for = request.headers.get("x-forwarded-for")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        
        real_ip = request.headers.get("x-real-ip")
        if real_ip:
            return real_ip.strip()
        
        if request.client and hasattr(request.client, "host"):
            return request.client.host
        
        return "127.0.0.1"
    
    @staticmethod
    def parse_user_agent(ua_str: Optional[str]) -> UserAgentInfo:
        """使用 user-agents 库解析 User-Agent
        
        基于功能强大的第三方 user-agents 库，高精度解析 UA 信息，
        支持识别数千种设备、操作系统和浏览器。
        
        Args:
            ua_str: User-Agent 字符串
        
        Returns:
            UserAgentInfo 解析结果对象
        """
        
        if not ua_str:
            return UserAgentInfo(user_agent=ua_str)
        
        ua = parse(ua_str)

        # 👇 核心：按优先级判断设备类型
        if ua.is_pc:
            device_type = "PC"
        elif ua.is_mobile:
            device_type = "Mobile"
        elif ua.is_tablet:
            device_type = "Tablet"
        elif ua.is_bot:
            device_type = "Bot"
        else:
            device_type = "Unknown"
        
        return UserAgentInfo(
            user_agent=ua_str,
            browser=ua.browser.family + " " + ua.browser.version_string,
            os=ua.os.family + " " + ua.os.version_string,
            device_type=device_type,
        )
    
    @staticmethod
    def get_user_agent_info(request: Request) -> UserAgentInfo:
        """从 Request 对象中直接获取并解析 User-Agent
        
        是 parse_user_agent 方法的快捷方式，直接从请求头中读取 UA。
        
        Args:
            request: FastAPI 请求对象
        
        Returns:
            UserAgentInfo 解析结果对象
        """
        ua_str = request.headers.get("user-agent", "")
        return HttpUtils.parse_user_agent(ua_str)
