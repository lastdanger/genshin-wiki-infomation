"""
Monsters API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.conftest import create_monster


@pytest.mark.api
@pytest.mark.asyncio
class TestMonstersAPI:
    """Monsters API 测试类"""

    async def test_list_monsters(self, client: AsyncClient):
        """测试获取怪物列表"""
        response = await client.get("/api/v1/monsters")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_get_monster_by_id(self, client: AsyncClient, db_session: Session):
        """测试通过ID获取怪物"""
        monster = create_monster(
            db_session,
            name="Hilichurl",
            monster_type="Common",
            category="Hilichurl"
        )

        response = await client.get(f"/api/v1/monsters/{monster.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == monster.id
        assert data["name"] == "Hilichurl"

    async def test_create_monster(self, client: AsyncClient, sample_monster_data):
        """测试创建怪物"""
        response = await client.post("/api/v1/monsters", json=sample_monster_data)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data

    async def test_filter_monsters_by_type(
        self, client: AsyncClient, db_session: Session
    ):
        """测试按类型筛选怪物"""
        create_monster(db_session, name="Monster1", monster_type="Elite")
        create_monster(db_session, name="Monster2", monster_type="Common")
        create_monster(db_session, name="Monster3", monster_type="Elite")

        response = await client.get("/api/v1/monsters?monster_type=Elite")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_update_monster(self, client: AsyncClient, db_session: Session):
        """测试更新怪物"""
        monster = create_monster(db_session, name="Test Monster")

        update_data = {"description": "Updated description"}
        response = await client.put(
            f"/api/v1/monsters/{monster.id}",
            json=update_data
        )
        assert response.status_code == 200

    async def test_delete_monster(self, client: AsyncClient, db_session: Session):
        """测试删除怪物"""
        monster = create_monster(db_session, name="Test Monster")

        response = await client.delete(f"/api/v1/monsters/{monster.id}")
        assert response.status_code == 204
