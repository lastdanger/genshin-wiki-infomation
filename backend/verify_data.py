"""
验证数据库中的角色数据
"""
import asyncio
from sqlalchemy import select, func
from src.db.session import AsyncSessionLocal
from src.models.character import Character


async def verify_characters():
    """验证角色数据"""
    print("=== 验证角色数据 ===\n")

    async with AsyncSessionLocal() as session:
        # 统计角色总数
        count_stmt = select(func.count(Character.id))
        result = await session.execute(count_stmt)
        total = result.scalar()
        print(f"✅ 角色总数: {total}\n")

        # 按稀有度统计
        for rarity in [5, 4]:
            stmt = select(func.count(Character.id)).where(Character.rarity == rarity)
            result = await session.execute(stmt)
            count = result.scalar()
            print(f"   {rarity}星角色: {count}")

        print("\n=== 角色列表 ===\n")

        # 查询所有角色
        stmt = select(Character).order_by(Character.rarity.desc(), Character.name)
        result = await session.execute(stmt)
        characters = result.scalars().all()

        for char in characters:
            print(f"{char.rarity}⭐ {char.name:8} | {char.element:8} | {char.weapon_type:10} | {char.region}")

        print(f"\n=== 验证完成，共 {len(characters)} 个角色 ===")


if __name__ == "__main__":
    asyncio.run(verify_characters())
