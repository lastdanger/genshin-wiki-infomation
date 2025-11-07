"""
数据库连接和会话管理

提供异步数据库连接池和会话管理功能
"""
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool
from sqlalchemy import text
import structlog

from src.config import get_settings

logger = structlog.get_logger()
settings = get_settings()

# 异步数据库引擎
engine = create_async_engine(
    settings.database_url,
    echo=settings.environment == "development",  # 开发环境显示SQL
    pool_size=20,  # 连接池大小
    max_overflow=30,  # 最大溢出连接数
    pool_pre_ping=True,  # 连接前ping检查
    pool_recycle=3600,  # 连接回收时间（秒）
    poolclass=NullPool if settings.environment == "test" else None,  # 测试环境使用NullPool
)

# 异步会话工厂
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncSession:
    """
    获取数据库会话依赖注入函数

    用于FastAPI依赖注入，自动管理数据库会话的生命周期
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error("数据库会话异常", error=str(e))
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """
    初始化数据库连接

    在应用启动时调用，测试数据库连接是否正常
    """
    try:
        async with engine.begin() as conn:
            # 测试连接
            await conn.execute(text("SELECT 1"))
        logger.info("数据库连接测试成功")
    except Exception as e:
        logger.error("数据库连接失败", error=str(e))
        raise


async def close_db():
    """
    关闭数据库连接

    在应用关闭时调用，清理数据库连接池
    """
    await engine.dispose()
    logger.info("数据库连接池已关闭")