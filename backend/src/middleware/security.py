"""
安全中间件

提供基础的安全防护功能，包括请求头安全、请求大小限制等
"""
from fastapi import FastAPI, Request, HTTPException, status
from fastapi.responses import JSONResponse
import structlog
import time
from collections import defaultdict
from typing import Dict, Tuple

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# 简单的内存存储（生产环境应使用Redis）
request_counts: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))


class RateLimitMiddleware:
    """
    简单的速率限制中间件

    基于IP地址的请求频率限制，防止API滥用
    """

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # 1分钟窗口

    async def __call__(self, request: Request, call_next):
        # 获取客户端IP
        client_ip = self.get_client_ip(request)
        current_time = time.time()

        # 清理过期的请求记录
        self.cleanup_expired_records(current_time)

        # 检查当前IP的请求频率
        if self.is_rate_limited(client_ip, current_time):
            logger.warning(
                "API请求频率超限",
                client_ip=client_ip,
                requests_per_minute=self.requests_per_minute
            )
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "success": False,
                    "error": "请求频率过高",
                    "message": f"请求频率限制为每分钟{self.requests_per_minute}次，请稍后重试"
                }
            )

        # 记录当前请求
        request_counts[client_ip][current_time] = 1

        response = await call_next(request)
        return response

    def get_client_ip(self, request: Request) -> str:
        """获取客户端真实IP地址"""
        # 检查代理头
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()

        real_ip = request.headers.get("X-Real-IP")
        if real_ip:
            return real_ip

        # 回退到直接连接IP
        return request.client.host if request.client else "unknown"

    def cleanup_expired_records(self, current_time: float):
        """清理过期的请求记录"""
        cutoff_time = current_time - self.window_size

        for ip in list(request_counts.keys()):
            timestamps = request_counts[ip]
            # 删除过期的时间戳
            expired_keys = [ts for ts in timestamps.keys() if ts < cutoff_time]
            for key in expired_keys:
                del timestamps[key]

            # 如果该IP没有记录了，删除整个条目
            if not timestamps:
                del request_counts[ip]

    def is_rate_limited(self, client_ip: str, current_time: float) -> bool:
        """检查IP是否超过速率限制"""
        window_start = current_time - self.window_size
        recent_requests = len([
            ts for ts in request_counts[client_ip].keys()
            if ts > window_start
        ])

        return recent_requests >= self.requests_per_minute


def setup_security_middleware(app: FastAPI) -> None:
    """
    设置安全中间件

    Args:
        app: FastAPI应用实例
    """

    @app.middleware("http")
    async def security_headers_middleware(request: Request, call_next):
        """添加安全响应头"""
        response = await call_next(request)

        # 添加安全头
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # 生产环境添加HTTPS相关头
        if settings.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response

    @app.middleware("http")
    async def request_size_limit_middleware(request: Request, call_next):
        """请求大小限制中间件"""
        # 检查Content-Length头
        content_length = request.headers.get("Content-Length")
        if content_length:
            content_length = int(content_length)
            max_size = 10 * 1024 * 1024  # 10MB限制

            if content_length > max_size:
                logger.warning(
                    "请求体过大",
                    content_length=content_length,
                    max_size=max_size,
                    path=request.url.path
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "success": False,
                        "error": "请求体过大",
                        "message": f"请求体大小不能超过{max_size // 1024 // 1024}MB"
                    }
                )

        return await call_next(request)

    # 添加速率限制中间件（开发环境放宽限制）
    rate_limit = 120 if settings.environment == "development" else 60
    rate_limit_middleware = RateLimitMiddleware(requests_per_minute=rate_limit)
    app.middleware("http")(rate_limit_middleware)

    logger.info(
        "安全中间件配置完成",
        rate_limit_per_minute=rate_limit,
        environment=settings.environment
    )