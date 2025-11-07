"""
Weapons API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.conftest import create_weapon


@pytest.mark.api
@pytest.mark.asyncio
class TestWeaponsAPI:
    """Weapons API 测试类"""

    async def test_list_weapons_empty(self, client: AsyncClient):
        """测试获取空武器列表"""
        response = await client.get("/api/v1/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 0

    async def test_list_weapons(self, client: AsyncClient, db_session: Session):
        """测试获取武器列表"""
        create_weapon(db_session, name="Wolf's Gravestone", weapon_type="Claymore")
        create_weapon(db_session, name="Aquila Favonia", weapon_type="Sword")

        response = await client.get("/api/v1/weapons")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_get_weapon_by_id(self, client: AsyncClient, db_session: Session):
        """测试通过ID获取武器"""
        weapon = create_weapon(
            db_session,
            name="Wolf's Gravestone",
            weapon_type="Claymore",
            rarity=5
        )

        response = await client.get(f"/api/v1/weapons/{weapon.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == weapon.id
        assert data["name"] == "Wolf's Gravestone"

    async def test_filter_weapons_by_type(
        self, client: AsyncClient, db_session: Session
    ):
        """测试按武器类型筛选"""
        create_weapon(db_session, name="Sword1", weapon_type="Sword")
        create_weapon(db_session, name="Claymore1", weapon_type="Claymore")
        create_weapon(db_session, name="Sword2", weapon_type="Sword")

        response = await client.get("/api/v1/weapons?weapon_type=Sword")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_create_weapon(self, client: AsyncClient, sample_weapon_data):
        """测试创建武器"""
        response = await client.post("/api/v1/weapons", json=sample_weapon_data)
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_weapon_data["name"]
        assert "id" in data

    async def test_update_weapon(self, client: AsyncClient, db_session: Session):
        """测试更新武器"""
        weapon = create_weapon(db_session, name="Test Weapon")

        update_data = {"description": "Updated description"}
        response = await client.put(
            f"/api/v1/weapons/{weapon.id}",
            json=update_data
        )
        assert response.status_code == 200

    async def test_delete_weapon(self, client: AsyncClient, db_session: Session):
        """测试删除武器"""
        weapon = create_weapon(db_session, name="Test Weapon")

        response = await client.delete(f"/api/v1/weapons/{weapon.id}")
        assert response.status_code == 204
