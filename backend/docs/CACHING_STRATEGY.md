# Redis 缓存策略文档

本文档说明原神游戏信息网站后端的 Redis 缓存策略和实现。

## 目录

- [概述](#概述)
- [缓存配置](#缓存配置)
- [缓存装饰器](#缓存装饰器)
- [缓存过期策略](#缓存过期策略)
- [缓存失效](#缓存失效)
- [缓存监控](#缓存监控)
- [最佳实践](#最佳实践)

## 概述

Redis 缓存系统提供：

1. **CacheManager** - 缓存管理器
2. **@cached** - 缓存装饰器
3. **@cache_invalidate** - 缓存失效装饰器
4. **CacheKeys** - 缓存键常量
5. **缓存统计** - 命中率监控

## 缓存配置

### 环境变量

```env
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=300  # 默认过期时间（秒）
```

### 配置说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| REDIS_URL | Redis 连接 URL | redis://localhost:6379/0 |
| REDIS_CACHE_TTL | 默认缓存过期时间 | 300 秒 |

## 缓存装饰器

### @cached 装饰器

用于缓存函数返回值。

#### 基本用法

```python
from src.cache.cache_manager import cached, CacheKeys
from datetime import timedelta

@cached(ttl=300, key_prefix=CacheKeys.CHARACTER_LIST)
async def get_character_list(page: int, per_page: int):
    # 查询数据库
    characters = await fetch_characters_from_db(page, per_page)
    return characters
```

#### 参数说明

- **ttl**: 缓存过期时间（秒或 timedelta）
- **key_prefix**: 缓存键前缀
- **invalidate_on_error**: 发生错误时是否清除缓存

#### 缓存键生成规则

缓存键格式：`genshin:{prefix}:{params}`

```python
# 示例：
# 函数调用：get_character_list(page=1, per_page=20)
# 生成的键：genshin:characters:list:1|per_page=20
```

## 缓存过期策略

根据数据更新频率和查询频率，设置不同的过期时间。

| 数据类型 | 过期时间 | 说明 |
|---------|---------|------|
| 角色列表 | 5 分钟 | 经常查询，偶尔更新 |
| 角色详情 | 10 分钟 | 读多写少 |
| 武器列表 | 5 分钟 | 经常查询 |
| 武器详情 | 10 分钟 | 读多写少 |
| 圣遗物列表 | 10 分钟 | 更新较少 |
| 圣遗物详情 | 15 分钟 | 更新很少 |
| 怪物列表 | 10 分钟 | 更新较少 |
| 怪物详情 | 15 分钟 | 更新很少 |
| 搜索结果 | 3 分钟 | 实时性要求高 |
| 统计数据 | 30 分钟 | 更新很少 |

## 缓存失效

### 自动失效

使用 `@cache_invalidate` 装饰器在数据更新时自动清除相关缓存。

```python
from src.cache.cache_manager import cache_invalidate, CacheKeys

@cache_invalidate(pattern=f"{CacheKeys.CHARACTER_LIST}:*")
async def create_character(character_data: CharacterCreate):
    # 创建角色
    character = await db.create(character_data)
    # 函数执行成功后，自动清除所有角色列表缓存
    return character

@cache_invalidate(pattern=f"{CacheKeys.CHARACTER_DETAIL}:*")
async def update_character(character_id: int, update_data: CharacterUpdate):
    # 更新角色
    character = await db.update(character_id, update_data)
    # 自动清除该角色的详情缓存
    return character
```

### 手动失效

```python
from src.cache.cache_manager import cache_manager

# 清除特定模式的缓存
await cache_manager.invalidate_pattern("characters:*")

# 清除特定实体的缓存
await cache_manager.invalidate_entity("characters", entity_id=123)

# 清除所有角色相关缓存
await cache_manager.invalidate_pattern("characters:*")
```

### 批量失效

```python
# 清除多个相关缓存
patterns = [
    f"{CacheKeys.CHARACTER_LIST}:*",
    f"{CacheKeys.CHARACTER_DETAIL}:*{character_id}*",
    f"{CacheKeys.CHARACTER_SKILLS}:*{character_id}*",
]

for pattern in patterns:
    await cache_manager.invalidate_pattern(pattern)
```

## 缓存监控

### 获取缓存统计

```python
from src.cache.cache_manager import cache_manager

# 获取统计信息
stats = cache_manager.get_stats()

# 返回值示例：
{
    "hits": 1250,
    "misses": 350,
    "sets": 350,
    "deletes": 25,
    "total_requests": 1600,
    "hit_rate": 78.13
}
```

### 重置统计

```python
cache_manager.reset_stats()
```

### 监控 API 端点

添加缓存统计端点：

```python
@router.get("/cache/stats")
async def get_cache_stats():
    """获取缓存统计信息"""
    stats = cache_manager.get_stats()

    # 获取 Redis 服务器信息
    redis_info = await cache_manager.redis.get_info()

    return {
        "success": True,
        "data": {
            "cache_stats": stats,
            "redis_info": {
                "used_memory": redis_info.get("used_memory_human"),
                "connected_clients": redis_info.get("connected_clients"),
                "uptime_in_days": redis_info.get("uptime_in_days"),
            }
        }
    }
```

## 最佳实践

### 1. 为不同场景选择合适的 TTL

```python
# 热门数据，短 TTL
@cached(ttl=180)  # 3 分钟
async def get_popular_characters():
    pass

# 稳定数据，长 TTL
@cached(ttl=1800)  # 30 分钟
async def get_game_mechanics():
    pass

# 实时性要求高，短 TTL
@cached(ttl=60)  # 1 分钟
async def search_characters(keyword: str):
    pass
```

### 2. 合理使用缓存键前缀

```python
from src.cache.cache_manager import CacheKeys

# 使用预定义的常量
@cached(key_prefix=CacheKeys.CHARACTER_LIST)
async def get_characters():
    pass

# 自定义前缀
@cached(key_prefix="characters:recommended")
async def get_recommended_characters():
    pass
```

### 3. 数据更新时清除缓存

```python
@cache_invalidate(pattern=f"{CacheKeys.CHARACTER_LIST}:*")
@cache_invalidate(pattern=f"{CacheKeys.CHARACTER_DETAIL}:*{character_id}*")
async def update_character(character_id: int, data: CharacterUpdate):
    # 更新操作
    result = await db.update(character_id, data)
    # 多个装饰器会依次清除相关缓存
    return result
```

### 4. 异常处理

```python
@cached(ttl=300, invalidate_on_error=True)
async def get_external_data():
    try:
        data = await fetch_from_external_api()
        return data
    except Exception as e:
        # invalidate_on_error=True 会自动清除缓存
        logger.error("Failed to fetch data", error=e)
        raise
```

### 5. 缓存预热

```python
from src.cache.cache_manager import cache_manager, CACHE_WARMUP_CONFIG

# 应用启动时预热缓存
async def warm_up_cache():
    await cache_manager.warm_up_cache(CACHE_WARMUP_CONFIG)
```

### 6. 分页缓存策略

```python
# 每页单独缓存
@cached(ttl=300)
async def get_characters_page(page: int, per_page: int):
    # 缓存键会自动包含 page 和 per_page
    # genshin:characters:list:1|per_page=20
    return await fetch_page(page, per_page)
```

### 7. 避免缓存穿透

```python
@cached(ttl=300)
async def get_character_by_id(character_id: int):
    character = await db.get(character_id)

    # 即使数据不存在也缓存结果（避免频繁查询不存在的数据）
    if not character:
        return None  # 缓存 None 值

    return character
```

### 8. 缓存大对象时的注意事项

```python
# 对于大对象，考虑只缓存 ID 列表
@cached(ttl=300)
async def get_character_ids(filters: Dict):
    # 只返回 ID 列表，减少缓存占用
    return [char.id for char in await query_characters(filters)]

# 然后根据需要获取完整对象
async def get_full_characters(filters: Dict):
    ids = await get_character_ids(filters)
    return await db.get_by_ids(ids)
```

### 9. 监控缓存命中率

```python
# 定期检查缓存统计
stats = cache_manager.get_stats()

if stats["hit_rate"] < 70:
    logger.warning(
        "Cache hit rate is low",
        hit_rate=stats["hit_rate"]
    )
```

### 10. 使用缓存层级

```python
# L1: 应用内存缓存（快但容量小）
# L2: Redis 缓存（较快且容量大）
# L3: 数据库（慢但完整）

@cached(ttl=300)  # L2 缓存
async def get_character(character_id: int):
    # L3: 从数据库查询
    return await db.query(character_id)
```

## 性能指标

### 目标指标

| 指标 | 目标值 |
|------|--------|
| 缓存命中率 | > 80% |
| API 响应时间（有缓存） | < 50ms |
| API 响应时间（无缓存） | < 500ms |
| 缓存设置延迟 | < 10ms |
| 缓存获取延迟 | < 5ms |

### 监控建议

1. **实时监控**
   - 缓存命中率
   - API 响应时间
   - Redis 内存使用

2. **告警阈值**
   - 命中率 < 70%
   - 响应时间 > 1s
   - Redis 内存使用 > 80%

3. **定期审查**
   - 每周检查缓存效果
   - 根据实际情况调整 TTL
   - 优化缓存键设计

## 故障处理

### Redis 不可用

```python
# 缓存操作已经内置了异常处理
# Redis 不可用时会自动降级到直接查询数据库

@cached(ttl=300)
async def get_data():
    # Redis 失败时，会直接执行函数并返回结果
    return await fetch_from_db()
```

### 缓存雪崩

```python
# 使用随机 TTL 避免缓存同时过期
import random

ttl = 300 + random.randint(-30, 30)  # 270-330 秒

@cached(ttl=ttl)
async def get_data():
    pass
```

### 缓存击穿

```python
# 使用互斥锁（TODO: 未来实现）
# 或者设置永不过期的热点数据

@cached(ttl=86400)  # 24 小时
async def get_hot_data():
    pass
```

## 技术支持

如遇问题，请联系：
- Email: support@genshin-wiki.com
- Issues: https://github.com/lastdanger/genshin-wiki-infomation/issues
