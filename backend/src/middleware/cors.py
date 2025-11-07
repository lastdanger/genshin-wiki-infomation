"""
CORS 跨域资源共享中间件

配置允许的跨域访问规则，支持前端应用访问API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()


def setup_cors_middleware(app: FastAPI) -> None:
    """
    设置CORS中间件

    Args:
        app: FastAPI应用实例
    """
    # 开发环境允许所有来源，生产环境限制特定域名
    if settings.environment == "development":
        allowed_origins = ["*"]
        allow_credentials = False
    else:
        # 生产环境配置具体的允许域名
        allowed_origins = [
            "https://genshin-info.com",  # 生产域名
            "https://www.genshin-info.com",
            "https://genshin-info-staging.com",  # 测试域名
        ]
        allow_credentials = True

    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=allow_credentials,
        allow_methods=[
            "GET",      # 获取数据
            "POST",     # 创建数据（图片上传）
            "PUT",      # 更新数据
            "DELETE",   # 删除数据
            "OPTIONS",  # 预检请求
        ],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Requested-With",
            "X-Process-Time",
        ],
        expose_headers=[
            "X-Process-Time",  # 暴露处理时间头
            "X-Total-Count",   # 暴露总数头（用于分页）
        ],
        max_age=600,  # 预检请求缓存时间（秒）
    )

    logger.info(
        "CORS中间件配置完成",
        allowed_origins=allowed_origins,
        environment=settings.environment
    )