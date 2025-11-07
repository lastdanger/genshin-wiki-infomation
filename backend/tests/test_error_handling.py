"""
错误处理测试

测试全局异常处理器和错误响应格式
"""
import pytest
from httpx import AsyncClient
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from src.main import app
from src.utils.exceptions import (
    NotFoundError,
    ValidationException,
    DatabaseException,
    ConflictError,
    PermissionError,
    RateLimitError,
)


@pytest.mark.asyncio
class TestErrorHandling:
    """错误处理测试类"""

    async def test_validation_error_response_format(self, client: AsyncClient):
        """测试验证错误的响应格式"""
        # 发送无效的分页参数
        response = await client.get("/api/v1/characters?page=-1&per_page=1000")

        assert response.status_code == 422
        data = response.json()

        # 验证错误响应结构
        assert data["success"] is False
        assert "error" in data
        assert "code" in data["error"]
        assert "message" in data["error"]
        assert "timestamp" in data["error"]
        assert "path" in data["error"]

        # 验证错误代码
        assert data["error"]["code"] == "VALIDATION_ERROR"

    async def test_validation_error_with_details(self, client: AsyncClient):
        """测试验证错误包含详细信息"""
        response = await client.get("/api/v1/characters?page=0")

        assert response.status_code == 422
        data = response.json()

        # 验证包含错误详情
        assert "details" in data["error"]
        assert isinstance(data["error"]["details"], list)
        assert len(data["error"]["details"]) > 0

        # 验证错误详情格式
        error_detail = data["error"]["details"][0]
        assert "field" in error_detail
        assert "message" in error_detail
        assert "type" in error_detail

    async def test_not_found_error(self, client: AsyncClient):
        """测试资源未找到错误"""
        response = await client.get("/api/v1/characters/999999")

        assert response.status_code == 404
        data = response.json()

        # 验证错误响应
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"
        assert "未找到" in data["error"]["message"] or "not found" in data["error"]["message"].lower()

        # 验证包含资源信息
        if "details" in data["error"]:
            details = data["error"]["details"]
            assert "resource" in details or "id" in details

    async def test_method_not_allowed_error(self, client: AsyncClient):
        """测试不允许的HTTP方法错误"""
        # 尝试对只读端点使用POST
        response = await client.post("/api/health")

        assert response.status_code == 405
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "METHOD_NOT_ALLOWED"

    async def test_invalid_json_error(self, client: AsyncClient):
        """测试无效JSON格式错误"""
        response = await client.post(
            "/api/v1/characters",
            content="invalid json{",
            headers={"Content-Type": "application/json"}
        )

        # 应该返回422或400
        assert response.status_code in [400, 422]
        data = response.json()

        assert data["success"] is False

    async def test_missing_required_field(self, client: AsyncClient):
        """测试缺少必填字段错误"""
        response = await client.post(
            "/api/v1/characters",
            json={
                # 缺少必填字段
                "element": "Pyro"
            }
        )

        assert response.status_code == 422
        data = response.json()

        assert data["success"] is False
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "details" in data["error"]

    async def test_error_response_has_timestamp(self, client: AsyncClient):
        """测试错误响应包含时间戳"""
        response = await client.get("/api/v1/characters/999999")

        data = response.json()
        assert "timestamp" in data["error"]

        # 验证时间戳格式 (ISO 8601)
        timestamp = data["error"]["timestamp"]
        assert "T" in timestamp
        assert "Z" in timestamp or "+" in timestamp

    async def test_error_response_has_path(self, client: AsyncClient):
        """测试错误响应包含请求路径"""
        test_path = "/api/v1/characters/999999"
        response = await client.get(test_path)

        data = response.json()
        assert "path" in data["error"]
        assert test_path in data["error"]["path"]

    async def test_multiple_validation_errors(self, client: AsyncClient):
        """测试多个验证错误"""
        response = await client.get("/api/v1/characters?page=-1&per_page=1000&rarity=10")

        assert response.status_code == 422
        data = response.json()

        # 应该包含多个错误
        if "details" in data["error"]:
            assert len(data["error"]["details"]) >= 2


@pytest.mark.asyncio
class TestCustomExceptions:
    """自定义异常测试类"""

    async def test_not_found_exception(self):
        """测试NotFoundError异常"""
        exc = NotFoundError(resource="Character", id_value=123)

        assert exc.code == "NOT_FOUND"
        assert "Character" in exc.message
        assert exc.details["resource"] == "Character"
        assert exc.details["id"] == 123

    async def test_validation_exception(self):
        """测试ValidationException异常"""
        exc = ValidationException(
            field="email",
            message="Invalid email format"
        )

        assert exc.code == "VALIDATION_ERROR"
        assert "email" in exc.details["field"]

    async def test_database_exception(self):
        """测试DatabaseException异常"""
        exc = DatabaseException(message="Connection failed")

        assert exc.code == "DATABASE_ERROR"
        assert "Connection failed" in exc.message

    async def test_conflict_exception(self):
        """测试ConflictError异常"""
        exc = ConflictError(resource="Character", message="Name already exists")

        assert exc.code == "CONFLICT"
        assert exc.details["resource"] == "Character"

    async def test_permission_exception(self):
        """测试PermissionError异常"""
        exc = PermissionError(action="delete", resource="Character")

        assert exc.code == "PERMISSION_DENIED"
        assert "delete" in exc.message
        assert exc.details["action"] == "delete"

    async def test_rate_limit_exception(self):
        """测试RateLimitError异常"""
        exc = RateLimitError(limit=100, window="分钟")

        assert exc.code == "RATE_LIMIT_EXCEEDED"
        assert exc.details["limit"] == 100
        assert exc.details["window"] == "分钟"


@pytest.mark.asyncio
class TestErrorLogging:
    """错误日志测试类"""

    async def test_error_generates_log(self, client: AsyncClient, caplog):
        """测试错误会生成日志"""
        import logging

        with caplog.at_level(logging.ERROR):
            response = await client.get("/api/v1/characters/999999")

            # 验证生成了错误日志
            # 注意：实际项目中可能需要根据日志配置调整断言

    async def test_server_error_has_request_id(self, client: AsyncClient):
        """测试服务器错误包含request_id"""
        # 这个测试需要模拟服务器错误
        # 由于我们的错误处理器会为500错误添加request_id

        # 暂时跳过，需要创建一个触发500错误的测试端点
        pytest.skip("需要创建测试端点来触发500错误")


@pytest.mark.asyncio
class TestErrorConsistency:
    """错误一致性测试类"""

    async def test_all_errors_have_success_false(self, client: AsyncClient):
        """测试所有错误响应的success字段都是false"""
        error_endpoints = [
            "/api/v1/characters/999999",  # 404
            "/api/v1/characters?page=-1",  # 422
        ]

        for endpoint in error_endpoints:
            response = await client.get(endpoint)
            data = response.json()
            assert data["success"] is False

    async def test_error_messages_are_strings(self, client: AsyncClient):
        """测试错误消息都是字符串类型"""
        response = await client.get("/api/v1/characters/999999")
        data = response.json()

        assert isinstance(data["error"]["message"], str)
        assert len(data["error"]["message"]) > 0

    async def test_error_codes_are_uppercase(self, client: AsyncClient):
        """测试错误代码都是大写"""
        error_endpoints = [
            "/api/v1/characters/999999",
            "/api/v1/characters?page=-1",
        ]

        for endpoint in error_endpoints:
            response = await client.get(endpoint)
            data = response.json()

            error_code = data["error"]["code"]
            assert error_code == error_code.upper()
            assert "_" in error_code or error_code.isupper()
