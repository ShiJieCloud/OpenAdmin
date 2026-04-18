from fastapi import FastAPI

app = FastAPI(
    title="OpenAdmin 后台管理系统",
    description="FastAPI + Vue3 开源后台",
    version="1.0.0"
)

# 测试接口
@app.get("/")
def index():
    return {"msg": "OpenAdmin 后端运行成功！"}