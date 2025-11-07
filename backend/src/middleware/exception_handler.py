"""
全局异常处理中间件

统一处理应用中的所有异常，提供友好的错误响应
"""
import traceback
import uuid
from datetime import datetime, timezone
from typing import Union

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from src.utils.exceptions import (
    GenshinInfoException,
    DatabaseException,
    NotFoundError,
    ValidationException,
    ConflictError,
    PermissionError,
    RateLimitError,
)
import structlog

logger = structlog.get_logger(__name__)


def generate_request_id() -> str:
    """生成请求追踪 ID"""
    return str(uuid.uuid4())[:8]


def create_error_response(
    code: str,
    message: str,
    status_code: int,
    path: str,
    details: Union[dict, list, None] = None,
    request_id: str = None,
) -> JSONResponse:
    """
    创建统一格式的错误响应

    Args:
        code: 错误代码
        message: 错误消息
        status_code: HTTP状态码
        path: 请求路径
        details: 错误详情
        request_id: 请求追踪ID

    Returns:
        JSONResponse: 格式化的错误响应
    """
    error_data = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "path": path,
        }
    }

    if details:
        error_data["error"]["details"] = details

    if request_id:
        error_data["error"]["request_id"] = request_id

    return JSONResponse(
        status_code=status_code,
        content=error_data
    )


async def genshin_info_exception_handler(
    request: Request,
    exc: GenshinInfoException
) -> JSONResponse:
    """
    处理自定义业务异常

    Args:
        request: FastAPI请求对象
        exc: 自定义异常实例

    Returns:
        JSONResponse: 错误响应
    """
    request_id = generate_request_id()

    # 根据异常类型确定HTTP状态码
    status_code_map = {
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        ValidationException: status.HTTP_422_UNPROCESSABLE_ENTITY,
        PermissionError: status.HTTP_403_FORBIDDEN,
        RateLimitError: status.HTTP_429_TOO_MANY_REQUESTS,
        DatabaseException: status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_code_map.get(
        type(exc),
        status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    # 记录错误日志
    logger.error(
        f"Business exception occurred",
        exc_info=exc,
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
            "error_code": exc.code,
            "error_message": exc.message,
            "error_details": exc.details,
        }
    )

    return create_error_response(
        code=exc.code or "INTERNAL_ERROR",
        message=exc.message,
        status_code=status_code,
        path=str(request.url.path),
        details=exc.details,
        request_id=request_id
    )


async def validation_exception_handler(
    request: Request,
    exc: RequestValidationError
) -> JSONResponse:
    """
    处理请求验证异常（FastAPI自动验证）

    Args:
        request: FastAPI请求对象
        exc: 验证异常实例

    Returns:
        JSONResponse: 错误响应
    """
    request_id = generate_request_id()

    # 格式化验证错误详情
    errors = []
    for error in exc.errors():
        error_detail = {
            "field": ".".join(str(loc) for loc in error["loc"][1:]),  # 跳过'body'
            "message": error["msg"],
            "type": error["type"]
        }
        if "ctx" in error:
            error_detail["context"] = error["ctx"]
        errors.append(error_detail)

    logger.warning(
        f"Request validation failed",
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
            "errors": errors,
        }
    )

    return create_error_response(
        code="VALIDATION_ERROR",
        message="请求数据验证失败",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        path=str(request.url.path),
        details=errors,
        request_id=request_id
    )


async def http_exception_handler(
    request: Request,
    exc: StarletteHTTPException
) -> JSONResponse:
    """
    处理HTTP异常

    Args:
        request: FastAPI请求对象
        exc: HTTP异常实例

    Returns:
        JSONResponse: 错误响应
    """
    request_id = generate_request_id()

    # 根据状态码确定错误代码
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        429: "RATE_LIMIT_EXCEEDED",
        500: "INTERNAL_SERVER_ERROR",
        502: "BAD_GATEWAY",
        503: "SERVICE_UNAVAILABLE",
    }

    code = code_map.get(exc.status_code, "HTTP_ERROR")

    logger.error(
        f"HTTP exception occurred",
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
            "status_code": exc.status_code,
            "detail": exc.detail,
        }
    )

    return create_error_response(
        code=code,
        message=str(exc.detail),
        status_code=exc.status_code,
        path=str(request.url.path),
        request_id=request_id
    )


async def sqlalchemy_exception_handler(
    request: Request,
    exc: SQLAlchemyError
) -> JSONResponse:
    """
    处理SQLAlchemy数据库异常

    Args:
        request: FastAPI请求对象
        exc: SQLAlchemy异常实例

    Returns:
        JSONResponse: 错误响应
    """
    request_id = generate_request_id()

    logger.error(
        f"Database error occurred",
        exc_info=exc,
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
        }
    )

    # 不暴露数据库错误详情给客户端
    return create_error_response(
        code="DATABASE_ERROR",
        message="数据库操作失败，请稍后重试",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        path=str(request.url.path),
        request_id=request_id
    )


async def unhandled_exception_handler(
    request: Request,
    exc: Exception
) -> JSONResponse:
    """
    处理所有未捕获的异常

    Args:
        request: FastAPI请求对象
        exc: 异常实例

    Returns:
        JSONResponse: 错误响应
    """
    request_id = generate_request_id()

    # 记录完整的异常堆栈
    logger.critical(
        f"Unhandled exception occurred",
        exc_info=exc,
        extra={
            "request_id": request_id,
            "path": str(request.url.path),
            "method": request.method,
            "exception_type": type(exc).__name__,
            "traceback": traceback.format_exc(),
        }
    )

    # 不暴露内部错误详情
    return create_error_response(
        code="INTERNAL_SERVER_ERROR",
        message="服务器内部错误，我们正在处理此问题",
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        path=str(request.url.path),
        request_id=request_id
    )


def register_exception_handlers(app):
    """
    注册所有异常处理器到FastAPI应用

    Args:
        app: FastAPI应用实例
    """
    # 自定义业务异常
    app.add_exception_handler(GenshinInfoException, genshin_info_exception_handler)

    # 请求验证异常
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # HTTP异常
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)

    # 数据库异常
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

    # 未处理的异常
    app.add_exception_handler(Exception, unhandled_exception_handler)

    logger.info("Exception handlers registered successfully")
