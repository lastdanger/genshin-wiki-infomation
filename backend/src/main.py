"""
原神游戏信息网站 - FastAPI 应用主入口

提供角色、武器、圣遗物、怪物、游戏机制等信息的 RESTful API 服务
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import structlog

from src.config import get_settings
from src.middleware.cors import setup_cors_middleware
from src.middleware.security import setup_security_middleware
from src.db.session import init_db
from src.utils.logging import setup_logging

# 导入路由模块
from src.api.health import router as health_router
from src.api.characters import router as characters_router
from src.api.weapons import router as weapons_router
from src.api.artifacts import router as artifacts_router
from src.api.monsters import router as monsters_router
from src.api.game_mechanics import router as game_mechanics_router
from src.api.images import router as images_router
from src.api.search import router as search_router

settings = get_settings()
logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在启动原神游戏信息网站API服务...")

    # 初始化数据库连接
    await init_db()
    logger.info("数据库连接初始化完成")

    yield

    # 关闭时清理
    logger.info("正在关闭API服务...")


# 创建FastAPI应用实例
app = FastAPI(
    title="原神游戏信息网站 API",
    description="提供原神角色、武器、圣遗物、怪物等游戏信息的统一查询接口",
    version="1.0.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    lifespan=lifespan,
    openapi_tags=[
        {
            "name": "角色 Characters",
            "description": "角色基础信息、技能天赋、推荐配装"
        },
        {
            "name": "武器 Weapons",
            "description": "武器属性、特效、角色推荐"
        },
        {
            "name": "圣遗物 Artifacts",
            "description": "圣遗物套装效果、词条推荐"
        },
        {
            "name": "怪物 Monsters",
            "description": "怪物信息、弱点、对策"
        },
        {
            "name": "游戏机制 Game Mechanics",
            "description": "游戏机制说明、攻略指南"
        },
        {
            "name": "图片 Images",
            "description": "官方图片、用户上传"
        },
        {
            "name": "搜索 Search",
            "description": "统一搜索接口"
        },
        {
            "name": "系统 System",
            "description": "健康检查、状态监控"
        }
    ]
)

# 设置日志
setup_logging()

# 设置中间件
setup_cors_middleware(app)
setup_security_middleware(app)

# 请求处理时间记录中间件
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """记录请求处理时间"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # 添加处理时间到响应头
    if hasattr(response, 'headers'):
        response.headers["X-Process-Time"] = str(process_time)

    # 记录慢请求（超过1秒）
    if process_time > 1.0:
        logger.warning(
            "慢请求检测",
            path=request.url.path,
            method=request.method,
            process_time=process_time
        )

    return response


# 全局异常处理器
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """全局异常处理"""
    logger.error(
        "未处理的异常",
        path=request.url.path,
        method=request.method,
        error=str(exc),
        exc_info=True
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": "服务器内部错误",
            "message": "请稍后重试，如问题持续请联系管理员"
        }
    )


# 注册API路由
app.include_router(
    health_router,
    prefix="/api",
    tags=["系统 System"]
)

app.include_router(
    characters_router,
    prefix="/api/characters",
    tags=["角色 Characters"]
)

app.include_router(
    weapons_router,
    prefix="/api/weapons",
    tags=["武器 Weapons"]
)

app.include_router(
    artifacts_router,
    prefix="/api/artifacts",
    tags=["圣遗物 Artifacts"]
)

app.include_router(
    monsters_router,
    prefix="/api/monsters",
    tags=["怪物 Monsters"]
)

app.include_router(
    game_mechanics_router,
    prefix="/api/game-mechanics",
    tags=["游戏机制 Game Mechanics"]
)

app.include_router(
    images_router,
    prefix="/api/images",
    tags=["图片 Images"]
)

app.include_router(
    search_router,
    prefix="/api/search",
    tags=["搜索 Search"]
)


@app.get("/", include_in_schema=False)
async def root():
    """根路径重定向到API文档"""
    return {
        "message": "原神游戏信息网站 API",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.environment == "development",
        log_level="info"
    )