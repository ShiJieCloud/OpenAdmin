from typing import Dict, Optional, Any
from fastapi import Request, Response
from user_agents import parse
from app.schemas.common import UserAgentInfo, IPLocationInfo
import httpx
import json
from starlette.datastructures import FormData, UploadFile


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
            device_type = "PHONE"
        elif ua.is_tablet:
            device_type = "PAD"
        elif ua.is_bot:
            device_type = "ROBOT"
        else:
            device_type = "UNKNOWN"
        
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

    @staticmethod
    def get_ip_location(ip: str) -> IPLocationInfo:
        """根据 IP 地址获取归属地信息
        
        使用 ip-api.com 接口获取 IP 归属地和运营商信息。
        
        Args:
            ip: IP 地址字符串
        
        Returns:
            IPLocationInfo 对象，包含国家、省份、城市、区县和运营商信息
        """

        url = f"http://ip-api.com/json/{ip}?lang=zh-CN"

        # 127.0.0.1 特殊处理
        if ip == "127.0.0.1":
            return IPLocationInfo(client_ip=ip)
        
        try:
            response = httpx.get(url, timeout=10)
            data = response.json()

            if data.get("status") != "success":
                return IPLocationInfo(client_ip=ip)
            ip_location = IPLocationInfo(
                client_ip=ip,
                ip_country=data.get("country", ""),
                ip_province=data.get("regionName", ""),
                ip_city=data.get("city", "")
            )

            return ip_location
        except Exception:
            return IPLocationInfo(client_ip=ip)
    

    @classmethod
    async def get_response_body(
            cls,
            response: Response,
            encoding: str = "utf-8"
    ) -> Optional[dict[str, any]]:
        """
        【公共方法】安全解析FastAPI响应体为字典格式
        :param response: FastAPI的Response对象
        :param encoding: 默认解码编码
        :return: 解析后的JSON字典，非JSON/解析失败返回None
        """
        body_bytes: bytes = b""

        try:
            # 1. 读取响应体字节数据（兼容普通/流式响应）
            body_bytes = await cls._read_response_bytes(response)

            # 2. 非JSON响应直接返回None
            if not cls._is_json_response(response):
                return None

            # 3. 安全解码字节数据
            body_str = cls._safe_decode_bytes(body_bytes, encoding)
            if not body_str:
                return None

            # 4. 安全解析JSON为字典（仅做解析，不提取字段）
            body_json = json.loads(body_str.strip())
            # 确保返回值是字典（避免JSON是数组/字符串等情况）
            return body_json if isinstance(body_json, dict) else None

        except Exception as e:
            print(f"Exception: {e}")
            return None

    @staticmethod
    async def _read_response_bytes(response: Response) -> bytes:
        """【内部公共方法】读取响应体字节数据（兼容普通/流式响应）"""
        # 优先读取已缓存的body
        if hasattr(response, "body") and response.body is not None:
            return response.body

        # 处理流式响应：消费迭代器并重建（避免后续读取耗尽）
        body_bytes = b""
        if hasattr(response, "body_iterator") and response.body_iterator is not None:
            async for chunk in response.body_iterator:
                if isinstance(chunk, bytes):
                    body_bytes += chunk
                else:
                    body_bytes += str(chunk).encode("utf-8")

            # 重建异步迭代器
            async def rebuild_iterator():
                yield body_bytes

            response.body_iterator = rebuild_iterator()

        return body_bytes

    @staticmethod
    def _is_json_response(response: Response) -> bool:
        """判断是否为JSON响应"""
        content_type = response.headers.get("Content-Type", "").lower()
        return "application/json" in content_type

    @staticmethod
    def _safe_decode_bytes(
            body_bytes: bytes,
            encoding: str
    ) -> Optional[str]:
        """解码字节数据"""
        if not body_bytes:
            return None

        try:
            return body_bytes.decode(encoding)
        except UnicodeDecodeError as e:
            print(f"UnicodeDecodeError: {e}")
            return None

    @classmethod
    async def get_request_params(cls, request: Request) -> Dict[str, Any]:
        """
        解析 FastAPI Request 对象的所有参数：路径参数 + 查询参数 + 请求体

        Args:
            request: FastAPI的Request对象
        Returns:
            完整参数字典（无参数则过滤对应键），格式：
            {
                "query_params": {},   # 查询参数（无则剔除）
                "request_body": Any   # 请求体（无则剔除，文件仅存文件名）
            }
        """
        params = {}

        # 1. 解析查询参数：非空则加入返回结果
        query_params = dict(request.query_params)
        if query_params:
            params["query_params"] = query_params

        # 2. 解析请求体：仅处理有请求体的方法，无有效内容则不加入
        if request.method in ["POST", "PUT", "PATCH", "DELETE"]:
            content_type = request.headers.get("Content-Type", "").lower()
            body = None
            try:
                # multipart/form-data 需要特殊处理，不能先调用 request.body()
                # 因为 request.form() 会消耗流，只能调用一次
                if "multipart/form-data" in content_type:
                    form_data = await request.form()
                    body = cls._parse_form_data(form_data)
                else:
                    # 保存原始请求体以便重置
                    raw_body = await request.body()
                    
                    if "application/json" in content_type and raw_body:
                        body = cls._parse_json_body(raw_body)
                    elif "application/x-www-form-urlencoded" in content_type and raw_body:
                        body = cls._parse_form_body(raw_body)
                    elif raw_body and raw_body.strip():
                        # 其他类型的请求体，直接返回原始字符串
                        body = raw_body.decode("utf-8")
                    
                    # 重置请求体，确保后续处理可以重新读取
                    if raw_body:
                        request._body = raw_body
            except Exception as e:
                body = f"请求体解析失败：{str(e)}"
                print(f"[HTTPUtils] 解析请求体失败: {str(e)}")

            # 请求体非空/非None时加入返回结果
            if body is not None and body != "":
                params["request_body"] = body

        return params
    
    @staticmethod
    def _parse_json_body(raw_body: bytes) -> Optional[Dict[str, Any]]:
        """解析JSON请求体"""
        try:
            import json
            return json.loads(raw_body.decode("utf-8"))
        except Exception:
            return None
    
    @staticmethod
    def _parse_form_body(raw_body: bytes) -> Dict[str, str]:
        """解析表单请求体"""
        try:
            from urllib.parse import parse_qs
            form_data = raw_body.decode("utf-8")
            parsed = parse_qs(form_data, keep_blank_values=True)
            # 将列表值转换为单个值
            return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
        except Exception:
            return {}

    @staticmethod
    def _parse_form_data(form_data: FormData) -> Dict[str, Any]:
        """解析multipart/form-data：仅保留文件名，不存储文件内容/类型/大小"""
        parsed = {}
        for key, value in form_data.items():
            if isinstance(value, UploadFile):
                # 仅存储文件名（核心修改：删除其他文件信息）
                parsed[key] = value.filename or "未知文件名"
            else:
                # 普通表单字段正常存储
                parsed[key] = value
        return parsed