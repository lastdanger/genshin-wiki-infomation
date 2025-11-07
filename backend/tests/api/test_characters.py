"""
Characters API 测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.orm import Session
from tests.conftest import create_character


@pytest.mark.api
@pytest.mark.asyncio
class TestCharactersAPI:
    """Characters API 测试类"""

    async def test_list_characters_empty(self, client: AsyncClient):
        """测试获取空角色列表"""
        response = await client.get("/api/v1/characters")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert len(data["items"]) == 0
        assert data["total"] == 0

    async def test_list_characters(self, client: AsyncClient, db_session: Session):
        """测试获取角色列表"""
        # 创建测试数据
        create_character(db_session, name="Diluc", element="Pyro")
        create_character(db_session, name="Kaeya", element="Cryo")
        create_character(db_session, name="Jean", element="Anemo")

        response = await client.get("/api/v1/characters")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 3
        assert len(data["items"]) == 3

    async def test_list_characters_pagination(self, client: AsyncClient, db_session: Session):
        """测试角色列表分页"""
        # 创建多个测试角色
        for i in range(15):
            create_character(
                db_session,
                name=f"Character{i}",
                name_cn=f"角色{i}"
            )

        # 测试第一页
        response = await client.get("/api/v1/characters?page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 15
        assert len(data["items"]) == 10
        assert data["page"] == 1
        assert data["page_size"] == 10
        assert data["total_pages"] == 2

        # 测试第二页
        response = await client.get("/api/v1/characters?page=2&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 5

    async def test_list_characters_filter_by_element(
        self, client: AsyncClient, db_session: Session
    ):
        """测试按元素筛选角色"""
        create_character(db_session, name="Diluc", element="Pyro")
        create_character(db_session, name="Kaeya", element="Cryo")
        create_character(db_session, name="Bennett", element="Pyro")

        response = await client.get("/api/v1/characters?element=Pyro")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for character in data["items"]:
            assert character["element"] == "Pyro"

    async def test_list_characters_filter_by_weapon_type(
        self, client: AsyncClient, db_session: Session
    ):
        """测试按武器类型筛选角色"""
        create_character(db_session, name="Diluc", weapon_type="Claymore")
        create_character(db_session, name="Kaeya", weapon_type="Sword")
        create_character(db_session, name="Noelle", weapon_type="Claymore")

        response = await client.get("/api/v1/characters?weapon_type=Claymore")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2

    async def test_list_characters_filter_by_rarity(
        self, client: AsyncClient, db_session: Session
    ):
        """测试按稀有度筛选角色"""
        create_character(db_session, name="Diluc", rarity=5)
        create_character(db_session, name="Bennett", rarity=4)
        create_character(db_session, name="Jean", rarity=5)

        response = await client.get("/api/v1/characters?rarity=5")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        for character in data["items"]:
            assert character["rarity"] == 5

    async def test_get_character_by_id(self, client: AsyncClient, db_session: Session):
        """测试通过ID获取角色"""
        character = create_character(
            db_session,
            name="Diluc",
            name_cn="迪卢克",
            element="Pyro",
            rarity=5
        )

        response = await client.get(f"/api/v1/characters/{character.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == character.id
        assert data["name"] == "Diluc"
        assert data["name_cn"] == "迪卢克"
        assert data["element"] == "Pyro"

    async def test_get_character_not_found(self, client: AsyncClient):
        """测试获取不存在的角色"""
        response = await client.get("/api/v1/characters/999999")
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    async def test_create_character(self, client: AsyncClient, sample_character_data):
        """测试创建角色"""
        response = await client.post(
            "/api/v1/characters",
            json=sample_character_data
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_character_data["name"]
        assert data["element"] == sample_character_data["element"]
        assert "id" in data

    async def test_create_character_duplicate_name(
        self, client: AsyncClient, db_session: Session, sample_character_data
    ):
        """测试创建重复名称的角色"""
        create_character(db_session, name=sample_character_data["name"])

        response = await client.post(
            "/api/v1/characters",
            json=sample_character_data
        )
        assert response.status_code == 400

    async def test_create_character_invalid_data(self, client: AsyncClient):
        """测试使用无效数据创建角色"""
        invalid_data = {
            "name": "",  # 空名称
            "element": "InvalidElement",  # 无效元素
            "rarity": 6  # 无效稀有度
        }

        response = await client.post("/api/v1/characters", json=invalid_data)
        assert response.status_code == 422

    async def test_update_character(
        self, client: AsyncClient, db_session: Session
    ):
        """测试更新角色"""
        character = create_character(db_session, name="Diluc", rarity=5)

        update_data = {
            "description": "Updated description",
            "description_cn": "更新的描述"
        }

        response = await client.put(
            f"/api/v1/characters/{character.id}",
            json=update_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["description"] == update_data["description"]

    async def test_update_character_not_found(self, client: AsyncClient):
        """测试更新不存在的角色"""
        response = await client.put(
            "/api/v1/characters/999999",
            json={"description": "Test"}
        )
        assert response.status_code == 404

    async def test_delete_character(
        self, client: AsyncClient, db_session: Session
    ):
        """测试删除角色"""
        character = create_character(db_session, name="Diluc")

        response = await client.delete(f"/api/v1/characters/{character.id}")
        assert response.status_code == 204

        # 验证角色已被删除
        response = await client.get(f"/api/v1/characters/{character.id}")
        assert response.status_code == 404

    async def test_delete_character_not_found(self, client: AsyncClient):
        """测试删除不存在的角色"""
        response = await client.delete("/api/v1/characters/999999")
        assert response.status_code == 404

    async def test_search_characters(
        self, client: AsyncClient, db_session: Session
    ):
        """测试搜索角色"""
        create_character(db_session, name="Diluc", name_cn="迪卢克")
        create_character(db_session, name="Diona", name_cn="迪奥娜")
        create_character(db_session, name="Jean", name_cn="琴")

        # 搜索名称包含 "Di" 的角色
        response = await client.get("/api/v1/characters?search=Di")
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
