from app.core.exceptions import register_exception_handlers
from app.core.middlewares import setup_cors
from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.schemas.base.response import ApiResponse
from app.config.app import app_config
from app.core.response import ResponseBuilder
from app.api.router import api_router

app = FastAPI(
    title=app_config.DOCS_TITLE,
    description=app_config.DOCS_DESCRIPTION,
    version=app_config.DOCS_VERSION,
    lifespan=lifespan,
    contact={
        "name": app_config.DOCS_CONTACT_NAME,
        "email": app_config.DOCS_CONTACT_EMAIL,
    },
    docs_url=app_config.DOCS_URL if app_config.DOCS_ENABLE else None,
    redoc_url=app_config.REDOC_URL if app_config.DOCS_ENABLE else None,
)

# 配置 CORS 跨域中间件
setup_cors(app)

# 注册全局异常处理器
register_exception_handlers(app)

# 注册API路由
app.include_router(api_router, prefix="/api")
