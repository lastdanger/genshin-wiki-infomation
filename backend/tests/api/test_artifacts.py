"""
Artifacts API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.conftest import create_artifact


@pytest.mark.api
@pytest.mark.asyncio
class TestArtifactsAPI:
    """Artifacts API 测试类"""

    async def test_list_artifacts(self, client: AsyncClient):
        """测试获取圣遗物列表"""
        response = await client.get("/api/v1/artifacts")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_artifact_by_id(self, client: AsyncClient, db_session: Session):
        """测试通过ID获取圣遗物"""
        artifact = create_artifact(
            db_session,
            set_name="Gladiator's Finale",
            max_rarity=5
        )

        response = await client.get(f"/api/v1/artifacts/{artifact.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == artifact.id

    async def test_create_artifact(self, client: AsyncClient, sample_artifact_data):
        """测试创建圣遗物"""
        response = await client.post("/api/v1/artifacts", json=sample_artifact_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data

    async def test_filter_artifacts_by_rarity(
        self, client: AsyncClient, db_session: Session
    ):
        """测试按稀有度筛选圣遗物"""
        create_artifact(db_session, set_name="Set1", max_rarity=5)
        create_artifact(db_session, set_name="Set2", max_rarity=4)
        create_artifact(db_session, set_name="Set3", max_rarity=5)

        response = await client.get("/api/v1/artifacts?max_rarity=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_delete_artifact(self, client: AsyncClient, db_session: Session):
        """测试删除圣遗物"""
        artifact = create_artifact(db_session, set_name="Test Set")

        response = await client.delete(f"/api/v1/artifacts/{artifact.id}")
        assert response.status_code == 204
