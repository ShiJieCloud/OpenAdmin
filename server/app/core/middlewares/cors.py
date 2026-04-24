from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.app import app_config


def setup_cors(app: FastAPI):
    """CORS 跨域中间件配置
    
    用于处理前端跨域请求，确保前端应用能够正常访问后端 API
    
    Args:
        app: FastAPI 应用实例
    
    配置说明：
    - allow_origins: 前端域名白名单
    - allow_credentials: 允许携带 Cookie、Token、Authorization 凭证
    - allow_methods: 允许的 HTTP 方法列表（GET/POST/PUT/DELETE/OPTIONS）
    - allow_headers: 允许自定义的请求头（Content-Type、Authorization、X-Request-Id）
    - expose_headers: 暴露后端自定义响应头给前端
    - max_age: 预检请求的缓存时间（秒），减少预检请求次数
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.CORS_ALLOW_ORIGINS,
        allow_credentials=app_config.CORS_ALLOW_CREDENTIALS,
        allow_methods=app_config.CORS_ALLOW_METHODS,
        allow_headers=app_config.CORS_ALLOW_HEADERS,
        expose_headers=app_config.CORS_EXPOSE_HEADERS,
        max_age=app_config.CORS_MAX_AGE,
    )
