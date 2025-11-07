"""
自定义异常类和错误处理

定义应用特定的异常类型，提供统一的错误处理机制
"""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class GenshinInfoException(Exception):
    """原神信息网站基础异常类"""

    def __init__(
        self,
        message: str,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(GenshinInfoException):
    """数据库相关异常"""

    def __init__(self, message: str = "数据库操作失败", **kwargs):
        super().__init__(message, code="DATABASE_ERROR", **kwargs)


class ExternalAPIException(GenshinInfoException):
    """外部API调用异常"""

    def __init__(self, api_name: str, message: str = "外部API调用失败", **kwargs):
        super().__init__(
            message,
            code="EXTERNAL_API_ERROR",
            details={"api_name": api_name, **kwargs.get("details", {})}
        )


class DataSyncException(GenshinInfoException):
    """数据同步异常"""

    def __init__(self, source: str, message: str = "数据同步失败", **kwargs):
        super().__init__(
            message,
            code="DATA_SYNC_ERROR",
            details={"source": source, **kwargs.get("details", {})}
        )


class ValidationException(GenshinInfoException):
    """数据验证异常"""

    def __init__(self, field: str, message: str = "数据验证失败", **kwargs):
        super().__init__(
            message,
            code="VALIDATION_ERROR",
            details={"field": field, **kwargs.get("details", {})}
        )


class NotFoundError(GenshinInfoException):
    """资源未找到异常"""

    def __init__(self, resource: str, id_value: Any = None, **kwargs):
        message = f"{resource}未找到"
        if id_value is not None:
            message += f": {id_value}"

        super().__init__(
            message,
            code="NOT_FOUND",
            details={"resource": resource, "id": id_value, **kwargs.get("details", {})}
        )


class ConflictError(GenshinInfoException):
    """资源冲突异常"""

    def __init__(self, resource: str, message: str = "资源冲突", **kwargs):
        super().__init__(
            message,
            code="CONFLICT",
            details={"resource": resource, **kwargs.get("details", {})}
        )


class PermissionError(GenshinInfoException):
    """权限不足异常"""

    def __init__(self, action: str, resource: str = None, **kwargs):
        message = f"无权限执行操作: {action}"
        if resource:
            message += f" on {resource}"

        super().__init__(
            message,
            code="PERMISSION_DENIED",
            details={"action": action, "resource": resource, **kwargs.get("details", {})}
        )


class RateLimitError(GenshinInfoException):
    """请求频率限制异常"""

    def __init__(self, limit: int, window: str = "分钟", **kwargs):
        super().__init__(
            f"请求频率超限，限制为每{window}{limit}次",
            code="RATE_LIMIT_EXCEEDED",
            details={"limit": limit, "window": window, **kwargs.get("details", {})}
        )


class FileUploadError(GenshinInfoException):
    """文件上传异常"""

    def __init__(self, reason: str = "文件上传失败", **kwargs):
        super().__init__(
            reason,
            code="FILE_UPLOAD_ERROR",
            **kwargs
        )


# HTTP异常转换器
def to_http_exception(exc: GenshinInfoException) -> HTTPException:
    """
    将自定义异常转换为HTTP异常

    Args:
        exc: 自定义异常实例

    Returns:
        HTTPException实例
    """
    status_code_map = {
        "NOT_FOUND": status.HTTP_404_NOT_FOUND,
        "CONFLICT": status.HTTP_409_CONFLICT,
        "VALIDATION_ERROR": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "PERMISSION_DENIED": status.HTTP_403_FORBIDDEN,
        "RATE_LIMIT_EXCEEDED": status.HTTP_429_TOO_MANY_REQUESTS,
        "FILE_UPLOAD_ERROR": status.HTTP_400_BAD_REQUEST,
        "DATABASE_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
        "EXTERNAL_API_ERROR": status.HTTP_503_SERVICE_UNAVAILABLE,
        "DATA_SYNC_ERROR": status.HTTP_500_INTERNAL_SERVER_ERROR,
    }

    status_code = status_code_map.get(exc.code, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return HTTPException(
        status_code=status_code,
        detail={
            "success": False,
            "error": exc.message,
            "code": exc.code,
            "details": exc.details
        }
    )


# 常用错误处理函数
def handle_database_error(operation: str, table: str = None) -> DatabaseException:
    """处理数据库错误的辅助函数"""
    message = f"数据库{operation}操作失败"
    if table:
        message += f": {table}表"

    return DatabaseException(
        message,
        details={"operation": operation, "table": table}
    )


def handle_not_found(entity_type: str, entity_id: Any = None) -> NotFoundError:
    """处理资源未找到错误的辅助函数"""
    return NotFoundError(
        resource=entity_type,
        id_value=entity_id
    )


def handle_validation_error(field: str, value: Any = None, reason: str = None) -> ValidationException:
    """处理验证错误的辅助函数"""
    message = f"字段 {field} 验证失败"
    if reason:
        message += f": {reason}"

    return ValidationException(
        field=field,
        message=message,
        details={"value": value, "reason": reason}
    )


def handle_external_api_error(
    api_name: str,
    endpoint: str,
    status_code: int = None,
    response_text: str = None
) -> ExternalAPIException:
    """处理外部API错误的辅助函数"""
    details = {"endpoint": endpoint}
    if status_code:
        details["status_code"] = status_code
    if response_text:
        details["response"] = response_text

    return ExternalAPIException(
        api_name=api_name,
        message=f"{api_name} API调用失败: {endpoint}",
        details=details
    )