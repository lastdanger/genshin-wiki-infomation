"""
错误响应的 Schema 定义

定义统一的错误响应格式
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    """错误详情"""

    field: Optional[str] = Field(None, description="出错的字段名")
    message: str = Field(..., description="错误详细信息")
    type: Optional[str] = Field(None, description="错误类型")

    class Config:
        json_schema_extra = {
            "example": {
                "field": "email",
                "message": "Invalid email format",
                "type": "value_error.email"
            }
        }


class ErrorResponse(BaseModel):
    """统一错误响应格式"""

    success: bool = Field(False, description="请求是否成功")
    error: Dict[str, Any] = Field(..., description="错误信息")

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "数据验证失败",
                    "details": [
                        {
                            "field": "name",
                            "message": "Name is required",
                            "type": "value_error.missing"
                        }
                    ],
                    "timestamp": "2025-11-07T12:00:00Z",
                    "path": "/api/v1/characters",
                    "request_id": "abc123"
                }
            }
        }


class ValidationErrorResponse(ErrorResponse):
    """验证错误响应"""

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "请求数据验证失败",
                    "details": [
                        {
                            "field": "element",
                            "message": "Invalid element type. Must be one of: Pyro, Hydro, Anemo, Electro, Dendro, Cryo, Geo",
                            "type": "value_error.enum"
                        }
                    ],
                    "timestamp": "2025-11-07T12:00:00Z",
                    "path": "/api/v1/characters"
                }
            }
        }


class NotFoundErrorResponse(ErrorResponse):
    """资源未找到错误响应"""

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "NOT_FOUND",
                    "message": "角色未找到: 123",
                    "details": {
                        "resource": "Character",
                        "id": 123
                    },
                    "timestamp": "2025-11-07T12:00:00Z",
                    "path": "/api/v1/characters/123"
                }
            }
        }


class InternalServerErrorResponse(ErrorResponse):
    """服务器内部错误响应"""

    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "服务器内部错误，请稍后重试",
                    "timestamp": "2025-11-07T12:00:00Z",
                    "path": "/api/v1/characters",
                    "request_id": "abc123"
                }
            }
        }
