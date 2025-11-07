"""
Health Check API 测试
"""
import pytest
from httpx import AsyncClient


@pytest.mark.api
@pytest.mark.asyncio
class TestHealthAPI:
    """Health Check API 测试类"""

    async def test_root_endpoint(self, client: AsyncClient):
        """测试根路径端点"""
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Welcome to Genshin Info API"
        assert "version" in data
        assert "docs_url" in data

    async def test_health_check(self, client: AsyncClient):
        """测试健康检查端点"""
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data
        assert "service" in data
        assert data["service"] == "genshin-info-api"

    async def test_health_detailed(self, client: AsyncClient):
        """测试详细健康检查端点"""
        response = await client.get("/health/detailed")
        assert response.status_code == 200
        data = response.json()

        # 检查基本字段
        assert "status" in data
        assert "timestamp" in data
        assert "service" in data
        assert "version" in data

        # 检查组件状态
        assert "components" in data
        components = data["components"]
        assert "database" in components
        assert "cache" in components

        # 检查数据库状态
        db_status = components["database"]
        assert "status" in db_status
        assert db_status["status"] in ["healthy", "unhealthy"]

    async def test_health_readiness(self, client: AsyncClient):
        """测试就绪检查端点"""
        response = await client.get("/health/ready")
        assert response.status_code in [200, 503]
        data = response.json()
        assert "ready" in data
        assert isinstance(data["ready"], bool)

    async def test_health_liveness(self, client: AsyncClient):
        """测试存活检查端点"""
        response = await client.get("/health/live")
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert "timestamp" in data

    async def test_version_endpoint(self, client: AsyncClient):
        """测试版本信息端点"""
        response = await client.get("/health/version")
        assert response.status_code == 200
        data = response.json()
        assert "version" in data
        assert "build_time" in data
        assert "environment" in data
