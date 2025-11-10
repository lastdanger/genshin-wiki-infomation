# 缓存应用示例

本文档提供 Redis 缓存在各个服务层的具体应用示例。

## 目录

- [Service 层缓存](#service-层缓存)
- [API 层缓存](#api-层缓存)
- [缓存失效示例](#缓存失效示例)
- [完整示例](#完整示例)

## Service 层缓存

### 角色服务缓存

```python
# src/services/character_service.py

from src.cache.cache_manager import cached, cache_invalidate, CacheKeys
from datetime import timedelta

class CharacterService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @cached(ttl=300, key_prefix=CacheKeys.CHARACTER_LIST)
    async def get_character_list(
        self,
        params: CharacterQueryParams
    ) -> Tuple[List[Character], int]:
        """
        获取角色列表（分页）- 带缓存

        缓存键示例：genshin:characters:list:1|per_page=20|element=Pyro
        TTL: 5分钟
        """
        # 查询数据库
        query = select(Character)

        # 应用过滤条件
        if params.element:
            query = query.where(Character.element == params.element)
        if params.weapon_type:
            query = query.where(Character.weapon_type == params.weapon_type)

        # 执行查询
        result = await self.db.execute(query)
        characters = result.scalars().all()

        return characters, len(characters)

    @cached(ttl=600, key_prefix=CacheKeys.CHARACTER_DETAIL)
    async def get_character_by_id(
        self,
        character_id: int,
        include_skills: bool = True
    ) -> Optional[Character]:
        """
        获取角色详情 - 带缓存

        缓存键示例：genshin:characters:detail:123|include_skills=True
        TTL: 10分钟
        """
        query = select(Character).where(Character.id == character_id)

        if include_skills:
            query = query.options(selectinload(Character.skills))

        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    @cache_invalidate(pattern=f"{CacheKeys.CHARACTER_LIST}:*")
    @cache_invalidate(pattern=f"{CacheKeys.CHARACTER_SEARCH}:*")
    async def create_character(
        self,
        character_data: CharacterCreate
    ) -> Character:
        """
        创建角色 - 自动清除列表缓存

        创建成功后会自动清除：
        - 所有角色列表缓存
        - 所有角色搜索缓存
        """
        character = Character(**character_data.dict())
        self.db.add(character)
        await self.db.commit()
        await self.db.refresh(character)

        return character

    @cache_invalidate(pattern=f"{CacheKeys.CHARACTER_DETAIL}:*")
    @cache_invalidate(pattern=f"{CacheKeys.CHARACTER_LIST}:*")
    async def update_character(
        self,
        character_id: int,
        update_data: CharacterUpdate
    ) -> Character:
        """
        更新角色 - 自动清除相关缓存

        更新成功后会自动清除：
        - 该角色的详情缓存
        - 所有角色列表缓存（因为列表可能包含更新的字段）
        """
        character = await self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError("Character", character_id)

        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(character, key, value)

        await self.db.commit()
        await self.db.refresh(character)

        return character

    @cache_invalidate(pattern=f"{CacheKeys.CHARACTER_DETAIL}:*")
    @cache_invalidate(pattern=f"{CacheKeys.CHARACTER_LIST}:*")
    async def delete_character(self, character_id: int) -> bool:
        """
        删除角色 - 自动清除相关缓存
        """
        character = await self.get_character_by_id(character_id)
        if not character:
            raise NotFoundError("Character", character_id)

        await self.db.delete(character)
        await self.db.commit()

        return True

    @cached(ttl=180, key_prefix=CacheKeys.CHARACTER_SEARCH)
    async def search_characters(
        self,
        keyword: str,
        limit: int = 20
    ) -> List[Character]:
        """
        搜索角色 - 带缓存

        缓存键示例：genshin:characters:search:diluc|limit=20
        TTL: 3分钟（搜索结果实时性要求较高）
        """
        query = select(Character).where(
            or_(
                Character.name.ilike(f"%{keyword}%"),
                Character.description.ilike(f"%{keyword}%")
            )
        ).limit(limit)

        result = await self.db.execute(query)
        return result.scalars().all()
```

### 武器服务缓存

```python
# src/services/weapon_service.py

from src.cache.cache_manager import cached, cache_invalidate, CacheKeys

class WeaponService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @cached(ttl=300, key_prefix=CacheKeys.WEAPON_LIST)
    async def get_weapon_list(
        self,
        page: int = 1,
        per_page: int = 20,
        weapon_type: Optional[str] = None,
        rarity: Optional[int] = None
    ) -> Tuple[List[Weapon], int]:
        """获取武器列表 - 带缓存（5分钟）"""
        query = select(Weapon)

        if weapon_type:
            query = query.where(Weapon.weapon_type == weapon_type)
        if rarity:
            query = query.where(Weapon.rarity == rarity)

        # 分页
        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        weapons = result.scalars().all()

        # 获取总数
        count_query = select(func.count(Weapon.id))
        if weapon_type:
            count_query = count_query.where(Weapon.weapon_type == weapon_type)
        if rarity:
            count_query = count_query.where(Weapon.rarity == rarity)

        total = await self.db.scalar(count_query)

        return weapons, total

    @cached(ttl=600, key_prefix=CacheKeys.WEAPON_DETAIL)
    async def get_weapon_by_id(self, weapon_id: int) -> Optional[Weapon]:
        """获取武器详情 - 带缓存（10分钟）"""
        result = await self.db.execute(
            select(Weapon).where(Weapon.id == weapon_id)
        )
        return result.scalar_one_or_none()

    @cache_invalidate(pattern=f"{CacheKeys.WEAPON_LIST}:*")
    async def create_weapon(self, weapon_data: WeaponCreate) -> Weapon:
        """创建武器 - 清除列表缓存"""
        weapon = Weapon(**weapon_data.dict())
        self.db.add(weapon)
        await self.db.commit()
        await self.db.refresh(weapon)
        return weapon
```

### 圣遗物服务缓存

```python
# src/services/artifact_service.py

from src.cache.cache_manager import cached, cache_invalidate, CacheKeys

class ArtifactService:
    def __init__(self, db_session: AsyncSession):
        self.db = db_session

    @cached(ttl=600, key_prefix=CacheKeys.ARTIFACT_LIST)
    async def get_artifact_list(
        self,
        page: int = 1,
        per_page: int = 20,
        max_rarity: Optional[int] = None
    ) -> Tuple[List[Artifact], int]:
        """获取圣遗物列表 - 带缓存（10分钟，更新较少）"""
        query = select(Artifact)

        if max_rarity:
            query = query.where(Artifact.max_rarity == max_rarity)

        offset = (page - 1) * per_page
        query = query.offset(offset).limit(per_page)

        result = await self.db.execute(query)
        artifacts = result.scalars().all()

        total = await self.db.scalar(
            select(func.count(Artifact.id))
        )

        return artifacts, total

    @cached(ttl=900, key_prefix=CacheKeys.ARTIFACT_DETAIL)
    async def get_artifact_by_id(self, artifact_id: int) -> Optional[Artifact]:
        """获取圣遗物详情 - 带缓存（15分钟，更新很少）"""
        result = await self.db.execute(
            select(Artifact).where(Artifact.id == artifact_id)
        )
        return result.scalar_one_or_none()
```

## API 层缓存

### 直接在路由中使用缓存

```python
# src/api/characters.py

from src.cache.cache_manager import cache_manager, CacheKeys

@router.get("/popular")
async def get_popular_characters():
    """获取热门角色 - 直接使用缓存管理器"""

    async def fetch_popular():
        # 实际的查询逻辑
        return await character_service.get_popular_characters()

    # 使用缓存管理器的 get_or_set 方法
    cache_key = f"genshin:{CacheKeys.CHARACTER_LIST}:popular"
    result = await cache_manager.get_or_set(
        cache_key,
        fetch_popular,
        ttl=3600  # 1小时
    )

    return {
        "success": True,
        "data": result
    }
```

## 缓存失效示例

### 手动清除缓存

```python
from src.cache.cache_manager import cache_manager

# 场景1：批量更新后清除所有相关缓存
async def batch_update_characters(updates: List[CharacterUpdate]):
    """批量更新角色"""
    for update in updates:
        await character_service.update_character(update.id, update)

    # 批量更新完成后，手动清除所有角色相关缓存
    await cache_manager.invalidate_pattern("characters:*")

    return {"success": True, "updated": len(updates)}

# 场景2：数据导入后清除缓存
async def import_characters_from_csv(file_path: str):
    """从CSV导入角色数据"""
    # 导入逻辑...
    imported_count = await import_csv(file_path)

    # 导入完成后清除缓存
    await cache_manager.invalidate_entity("characters")

    return {"success": True, "imported": imported_count}

# 场景3：定时任务更新后清除缓存
async def sync_characters_from_external_api():
    """从外部API同步角色数据"""
    # 同步逻辑...
    synced_data = await fetch_from_external_api()

    # 同步完成后清除相关缓存
    patterns = [
        f"{CacheKeys.CHARACTER_LIST}:*",
        f"{CacheKeys.CHARACTER_DETAIL}:*",
        f"{CacheKeys.CHARACTER_SEARCH}:*",
    ]

    for pattern in patterns:
        deleted = await cache_manager.invalidate_pattern(pattern)
        logger.info(f"清除缓存: {pattern}, 删除: {deleted} 个键")

    return synced_data
```

### 条件性缓存失效

```python
@cache_invalidate(pattern=f"{CacheKeys.CHARACTER_DETAIL}:*")
async def update_character_stats(
    character_id: int,
    new_stats: CharacterStats
):
    """
    更新角色属性

    只有当更新成功时才会清除缓存
    如果更新失败（抛出异常），缓存不会被清除
    """
    character = await db.get(character_id)
    if not character:
        raise NotFoundError("Character", character_id)

    # 验证数据
    if new_stats.hp < 0 or new_stats.attack < 0:
        raise ValidationException("stats", "属性值不能为负数")

    # 更新数据
    character.stats = new_stats
    await db.commit()

    # 函数成功返回后，装饰器会自动清除缓存
    return character
```

## 完整示例

### 带缓存的完整角色 API

```python
# src/api/characters.py

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.services.character_service import CharacterService
from src.schemas.character import (
    CharacterQueryParams, CharacterCreate, CharacterUpdate
)
from src.cache.cache_manager import cache_manager, CacheKeys

router = APIRouter()

async def get_character_service(
    db: AsyncSession = Depends(get_db)
) -> CharacterService:
    return CharacterService(db)

@router.get("/")
async def get_characters(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    element: Optional[str] = Query(None),
    weapon_type: Optional[str] = Query(None),
    rarity: Optional[int] = Query(None),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    获取角色列表

    自动缓存5分钟
    """
    params = CharacterQueryParams(
        page=page,
        per_page=per_page,
        element=element,
        weapon_type=weapon_type,
        rarity=rarity
    )

    # get_character_list 方法已经用 @cached 装饰，会自动缓存
    characters, total = await character_service.get_character_list(params)

    return {
        "success": True,
        "data": {
            "characters": [char.to_dict() for char in characters],
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total
            }
        }
    }

@router.get("/{character_id}")
async def get_character_detail(
    character_id: int = Path(..., gt=0),
    include_skills: bool = Query(True),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    获取角色详情

    自动缓存10分钟
    """
    # get_character_by_id 方法已经用 @cached 装饰
    character = await character_service.get_character_by_id(
        character_id,
        include_skills=include_skills
    )

    if not character:
        raise HTTPException(status_code=404, detail="角色不存在")

    return {
        "success": True,
        "data": character.to_dict()
    }

@router.post("/", status_code=201)
async def create_character(
    character_data: CharacterCreate,
    character_service: CharacterService = Depends(get_character_service)
):
    """
    创建角色

    创建成功后自动清除相关缓存
    """
    # create_character 方法已经用 @cache_invalidate 装饰
    # 会自动清除角色列表和搜索缓存
    character = await character_service.create_character(character_data)

    return {
        "success": True,
        "data": character.to_dict(),
        "message": "角色创建成功"
    }

@router.put("/{character_id}")
async def update_character(
    character_id: int = Path(..., gt=0),
    update_data: CharacterUpdate = ...,
    character_service: CharacterService = Depends(get_character_service)
):
    """
    更新角色

    更新成功后自动清除相关缓存
    """
    # update_character 方法已经用 @cache_invalidate 装饰
    character = await character_service.update_character(
        character_id,
        update_data
    )

    return {
        "success": True,
        "data": character.to_dict(),
        "message": "角色更新成功"
    }

@router.delete("/{character_id}", status_code=204)
async def delete_character(
    character_id: int = Path(..., gt=0),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    删除角色

    删除成功后自动清除相关缓存
    """
    await character_service.delete_character(character_id)
    return None

@router.get("/search")
async def search_characters(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    limit: int = Query(20, ge=1, le=100),
    character_service: CharacterService = Depends(get_character_service)
):
    """
    搜索角色

    自动缓存3分钟
    """
    # search_characters 方法已经用 @cached 装饰
    results = await character_service.search_characters(q, limit)

    return {
        "success": True,
        "data": {
            "keyword": q,
            "results": [char.to_dict() for char in results],
            "count": len(results)
        }
    }
```

## 缓存性能监控示例

```python
# 在 middleware 中记录缓存性能

@app.middleware("http")
async def cache_performance_middleware(request: Request, call_next):
    # 记录请求开始时的缓存统计
    stats_before = cache_manager.get_stats()

    # 处理请求
    response = await call_next(request)

    # 记录请求结束时的缓存统计
    stats_after = cache_manager.get_stats()

    # 计算这次请求的缓存使用情况
    hits_delta = stats_after["hits"] - stats_before["hits"]
    misses_delta = stats_after["misses"] - stats_before["misses"]

    # 添加到响应头
    response.headers["X-Cache-Hits"] = str(hits_delta)
    response.headers["X-Cache-Misses"] = str(misses_delta)

    if hits_delta + misses_delta > 0:
        request_hit_rate = hits_delta / (hits_delta + misses_delta) * 100
        response.headers["X-Cache-Hit-Rate"] = f"{request_hit_rate:.2f}%"

    return response
```

## 总结

缓存应用的关键点：

1. **Service 层使用 @cached 装饰器** - 自动缓存查询结果
2. **Service 层使用 @cache_invalidate 装饰器** - 自动清除相关缓存
3. **合理设置 TTL** - 根据数据更新频率和实时性要求
4. **统一使用 CacheKeys 常量** - 便于管理和清除
5. **监控缓存性能** - 定期检查命中率和响应时间
