from app.core import ResponseBuilder, register_exception_handlers, setup_cors
from fastapi import FastAPI
from app.core.lifespan import lifespan
from app.schemas.base.response import ApiResponse

app = FastAPI(
    title="OpenAdmin 后台管理系统",
    description="FastAPI + Vue3 开源后台",
    version="1.0.0",
    lifespan=lifespan
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
