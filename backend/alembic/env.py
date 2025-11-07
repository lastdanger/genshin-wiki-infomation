import asyncio
from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.append(str(Path(__file__).parent.parent))

# 导入模型
from src.models.base import Base
from src.models.character import Character
from src.models.character_skill import CharacterSkill
from src.models.character_talent import CharacterTalent
from src.models.weapon import Weapon
from src.models.artifact import Artifact
from src.models.artifact_piece import ArtifactPiece
from src.models.monster import Monster
from src.models.game_mechanic import GameMechanic
from src.models.image import Image
from src.models.character_weapon_recommendation import CharacterWeaponRecommendation
from src.models.character_artifact_recommendation import CharacterArtifactRecommendation

# 这是 Alembic Config 对象，它提供对值的访问
# 在 .ini 文件中使用。
config = context.config

# 解释配置文件以获得Python日志记录。
# 这行基本上配置了loggers。
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 为'autogenerate'支持添加你的模型的MetaData对象
target_metadata = Base.metadata

# 其他从myapp导入*这里也很合适


def run_migrations_offline() -> None:
    """以"离线"模式运行迁移。

    这为context配置了一个URL
    而不需要可用的引擎，尽管在这里需要引擎。

    通过跳过Engine创建，我们不需要在此连接到DBAPI，
    我们甚至不需要安装DBAPI。

    使用--sql标志调用：就是使用此函数。
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """以异步模式运行迁移。"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """以"在线"模式运行迁移。"""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()