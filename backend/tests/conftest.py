"""
Pytest 配置和共享 fixtures
"""
import os
import asyncio
from typing import AsyncGenerator, Generator
import pytest
from httpx import AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.main import app
from src.db.session import get_db
from src.models.base import Base
from src.config import get_settings

# 设置测试环境变量
os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["REDIS_URL"] = "redis://localhost:6379/1"

settings = get_settings()


# ============================================================================
# 数据库 Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """创建事件循环供整个测试会话使用"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
def db_engine():
    """创建测试数据库引擎 (每个测试函数独立)"""
    # 使用内存 SQLite 数据库进行测试
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 创建所有表
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine) -> Generator[Session, None, None]:
    """创建测试数据库会话"""
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=db_engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def override_get_db(db_session: Session):
    """覆盖数据库依赖注入"""
    async def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.clear()


# ============================================================================
# HTTP 客户端 Fixtures
# ============================================================================

@pytest.fixture(scope="function")
async def client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """创建测试 HTTP 客户端"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


# ============================================================================
# 测试数据 Fixtures
# ============================================================================

@pytest.fixture
def sample_character_data():
    """示例角色数据"""
    return {
        "name": "Test Character",
        "name_cn": "测试角色",
        "element": "Pyro",
        "weapon_type": "Sword",
        "rarity": 5,
        "region": "Mondstadt",
        "description": "A test character for unit testing",
        "description_cn": "用于单元测试的测试角色"
    }


@pytest.fixture
def sample_weapon_data():
    """示例武器数据"""
    return {
        "name": "Test Sword",
        "name_cn": "测试之剑",
        "weapon_type": "Sword",
        "rarity": 5,
        "base_attack": 46,
        "sub_stat_type": "CRIT Rate",
        "sub_stat_value": 7.2,
        "passive_name": "Test Passive",
        "passive_description": "Test passive description",
        "description": "A test sword",
        "description_cn": "测试用剑"
    }


@pytest.fixture
def sample_artifact_data():
    """示例圣遗物数据"""
    return {
        "set_name": "Test Artifact Set",
        "set_name_cn": "测试圣遗物套装",
        "max_rarity": 5,
        "two_piece_bonus": "Test 2-piece bonus",
        "four_piece_bonus": "Test 4-piece bonus",
        "description": "Test artifact set",
        "description_cn": "测试圣遗物套装"
    }


@pytest.fixture
def sample_monster_data():
    """示例怪物数据"""
    return {
        "name": "Test Monster",
        "name_cn": "测试怪物",
        "monster_type": "Elite",
        "category": "Abyss",
        "description": "A test monster",
        "description_cn": "测试怪物"
    }


# ============================================================================
# 辅助函数
# ============================================================================

def create_character(db: Session, **kwargs):
    """创建测试角色"""
    from src.models.character import Character

    default_data = {
        "name": "Test Character",
        "name_cn": "测试角色",
        "element": "Pyro",
        "weapon_type": "Sword",
        "rarity": 5,
        "region": "Mondstadt"
    }
    default_data.update(kwargs)

    character = Character(**default_data)
    db.add(character)
    db.commit()
    db.refresh(character)
    return character


def create_weapon(db: Session, **kwargs):
    """创建测试武器"""
    from src.models.weapon import Weapon

    default_data = {
        "name": "Test Weapon",
        "name_cn": "测试武器",
        "weapon_type": "Sword",
        "rarity": 5,
        "base_attack": 46
    }
    default_data.update(kwargs)

    weapon = Weapon(**default_data)
    db.add(weapon)
    db.commit()
    db.refresh(weapon)
    return weapon


def create_artifact(db: Session, **kwargs):
    """创建测试圣遗物"""
    from src.models.artifact import Artifact

    default_data = {
        "set_name": "Test Set",
        "set_name_cn": "测试套装",
        "max_rarity": 5
    }
    default_data.update(kwargs)

    artifact = Artifact(**default_data)
    db.add(artifact)
    db.commit()
    db.refresh(artifact)
    return artifact


def create_monster(db: Session, **kwargs):
    """创建测试怪物"""
    from src.models.monster import Monster

    default_data = {
        "name": "Test Monster",
        "name_cn": "测试怪物",
        "monster_type": "Elite",
        "category": "Abyss"
    }
    default_data.update(kwargs)

    monster = Monster(**default_data)
    db.add(monster)
    db.commit()
    db.refresh(monster)
    return monster
