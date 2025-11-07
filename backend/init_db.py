#!/usr/bin/env python3
"""
数据库初始化脚本

创建所有数据表结构
"""
import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from sqlalchemy import text
from src.db.session import engine
from src.models import Base  # 这会导入所有模型
import structlog

logger = structlog.get_logger()


async def init_database():
    """初始化数据库表结构"""
    try:
        logger.info("开始创建数据库表结构...")

        # 创建所有表
        async with engine.begin() as conn:
            # 确保PostgreSQL扩展存在（如果需要的话）
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\""))
                logger.info("UUID扩展检查完成")
            except Exception as e:
                logger.warning("UUID扩展设置失败，但继续执行", error=str(e))

            # 创建所有表
            await conn.run_sync(Base.metadata.create_all)
            logger.info("数据库表创建成功")

        # 验证表创建
        async with engine.begin() as conn:
            result = await conn.execute(
                text("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                """)
            )
            tables = [row[0] for row in result.fetchall()]
            logger.info("已创建的表", tables=tables)

        logger.info("数据库初始化完成！")

    except Exception as e:
        logger.error("数据库初始化失败", error=str(e))
        raise
    finally:
        await engine.dispose()


async def main():
    """主函数"""
    try:
        await init_database()
        print("✅ 数据库初始化成功！")
    except Exception as e:
        print(f"❌ 数据库初始化失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())