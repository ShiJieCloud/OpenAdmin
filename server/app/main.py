from app.core import ResponseBuilder, register_exception_handlers, setup_cors
from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.schemas.base.response import ApiResponse
from app.config.app import app_config

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

# 测试接口
@app.get("/", response_model=ApiResponse[str])
def index(username: str):
    return ResponseBuilder.success(username)

# 测试 RequestValidationError 异常
@app.get("/test-validation", response_model=ApiResponse[int])
def test_validation_error(item_id: int):
    """测试参数验证错误
    
    Args:
        item_id: 物品 ID，必须是整数
    
    Returns:
        ApiResponse: 测试结果
    """
    return ResponseBuilder.success(item_id)
