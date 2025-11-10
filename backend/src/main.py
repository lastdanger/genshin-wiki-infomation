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
from src.middleware.exception_handler import register_exception_handlers
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
from src.api.cache_stats import router as cache_router
from src.api.scraper import router as scraper_router

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


# API 文档描述
API_DESCRIPTION = """
## 原神游戏信息网站 API

提供原神游戏角色、武器、圣遗物、怪物等全方位信息的 RESTful API 服务。

### 主要功能

* **角色管理** - 查询角色信息、技能天赋、推荐配装
* **武器管理** - 查看武器属性、特效说明、适配角色
* **圣遗物管理** - 获取套装效果、词条推荐
* **怪物图鉴** - 了解怪物信息、弱点、对策攻略
* **数据搜索** - 跨模块的统一搜索功能

### API 特性

* 🚀 高性能异步架构
* 📊 完整的分页和筛选支持
* 🔍 强大的搜索功能
* 📝 标准化的响应格式
* ⚡ Redis 缓存加速
* 🛡️ 完善的错误处理

### 认证说明

当前版本为公开 API，无需认证。未来版本可能会添加 API Key 认证。

### 速率限制

* 未认证用户: 100 请求/分钟
* 认证用户: 1000 请求/分钟

### 技术支持

* 📧 Email: support@genshin-wiki.com
* 🐛 Issues: https://github.com/lastdanger/genshin-wiki-infomation/issues
* 📖 文档: https://docs.genshin-wiki.com

### 版本信息

当前版本: **v1.0.0**
更新日期: 2025-11-07
"""

# 创建FastAPI应用实例
app = FastAPI(
    title="原神游戏信息网站 API",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/api/docs" if settings.environment != "production" else None,
    redoc_url="/api/redoc" if settings.environment != "production" else None,
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "Genshin Wiki API Support",
        "url": "https://github.com/lastdanger/genshin-wiki-infomation",
        "email": "support@genshin-wiki.com"
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT"
    },
    openapi_tags=[
        {
            "name": "系统 System",
            "description": "**系统健康检查和监控**\n\n提供API服务状态、版本信息、健康检查等系统级接口。",
            "externalDocs": {
                "description": "了解更多关于系统监控",
                "url": "https://docs.genshin-wiki.com/system"
            }
        },
        {
            "name": "角色 Characters",
            "description": "**角色信息管理**\n\n获取原神角色的基础信息、技能天赋、命之座、推荐配装等完整数据。支持按元素、武器类型、稀有度等条件筛选。",
            "externalDocs": {
                "description": "角色数据说明",
                "url": "https://docs.genshin-wiki.com/characters"
            }
        },
        {
            "name": "武器 Weapons",
            "description": "**武器信息管理**\n\n查看武器的基础属性、副词条、特效说明、适配角色推荐等信息。支持按武器类型、稀有度筛选。",
            "externalDocs": {
                "description": "武器数据说明",
                "url": "https://docs.genshin-wiki.com/weapons"
            }
        },
        {
            "name": "圣遗物 Artifacts",
            "description": "**圣遗物套装管理**\n\n获取圣遗物套装的效果说明、推荐词条、适配角色等信息。",
            "externalDocs": {
                "description": "圣遗物数据说明",
                "url": "https://docs.genshin-wiki.com/artifacts"
            }
        },
        {
            "name": "怪物 Monsters",
            "description": "**怪物图鉴**\n\n查询怪物的基础信息、元素属性、弱点、掉落物、对策攻略等。支持按类型、类别筛选。",
            "externalDocs": {
                "description": "怪物数据说明",
                "url": "https://docs.genshin-wiki.com/monsters"
            }
        },
        {
            "name": "游戏机制 Game Mechanics",
            "description": "**游戏机制说明**\n\n元素反应、伤害计算、队伍搭配等游戏机制的详细说明和攻略。",
        },
        {
            "name": "图片 Images",
            "description": "**图片资源管理**\n\n角色、武器、圣遗物等的官方图片资源。",
        },
        {
            "name": "搜索 Search",
            "description": "**统一搜索接口**\n\n跨模块的全文搜索功能，可同时搜索角色、武器、圣遗物等。",
        },
        {
            "name": "爬虫 Scraper",
            "description": "**数据爬取管理**\n\n手动触发数据爬取、查看爬虫状态、爬取统计等。支持从多个数据源爬取角色、武器、圣遗物数据。",
        }
    ]
)

# 设置日志
setup_logging()

# 注册异常处理器
register_exception_handlers(app)

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

app.include_router(
    cache_router,
    prefix="/api/cache",
    tags=["系统 System"]
)

app.include_router(
    scraper_router,
    prefix="/api",
    tags=["爬虫 Scraper"]
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