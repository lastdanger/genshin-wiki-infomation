# API 使用指南

原神游戏信息网站 API 使用文档

## 🚀 快速开始

### API 基础地址

```
开发环境: http://localhost:8002
生产环境: https://api.genshin-wiki.com
```

### 交互式文档

- **Swagger UI**: http://localhost:8002/api/docs
- **ReDoc**: http://localhost:8002/api/redoc
- **OpenAPI JSON**: http://localhost:8002/api/openapi.json

## 📖 通用规范

### 请求格式

所有请求使用标准 HTTP 方法：
- `GET` - 获取资源
- `POST` - 创建资源
- `PUT` - 更新资源
- `DELETE` - 删除资源

### 响应格式

所有API返回统一的JSON格式：

**成功响应:**
```json
{
  "success": true,
  "data": {
    // 实际数据
  },
  "message": "操作成功"
}
```

**错误响应:**
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述",
    "details": {}
  }
}
```

### 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 请求成功 |
| 201 | 创建成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

### 分页参数

所有列表接口支持分页：

```
?page=1&per_page=20
```

分页响应包含：
```json
{
  "pagination": {
    "page": 1,
    "per_page": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

## 🎭 角色 API

### 获取角色列表

```http
GET /api/characters?page=1&per_page=20
```

**查询参数:**
- `page` (integer): 页码，默认 1
- `per_page` (integer): 每页数量，默认 20，最大 100
- `element` (string): 元素筛选 (Pyro, Hydro, Anemo, Electro, Cryo, Geo, Dendro)
- `weapon_type` (string): 武器类型筛选 (Sword, Claymore, Polearm, Bow, Catalyst)
- `rarity` (integer): 稀有度筛选 (4, 5)
- `region` (string): 地区筛选 (Mondstadt, Liyue, Inazuma, Sumeru, Fontaine)
- `search` (string): 搜索关键词
- `sort_by` (string): 排序字段，默认 name
- `sort_order` (string): 排序方向 (asc, desc)，默认 asc

**示例请求:**
```bash
curl -X GET "http://localhost:8002/api/characters?element=Pyro&rarity=5&page=1&per_page=10"
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "characters": [
      {
        "id": 1,
        "name": "Diluc",
        "name_cn": "迪卢克",
        "element": "Pyro",
        "weapon_type": "Claymore",
        "rarity": 5,
        "region": "Mondstadt",
        "icon_url": "https://example.com/diluc.png"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 3,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "message": "成功获取角色列表，共 3 个角色"
}
```

### 获取角色详情

```http
GET /api/characters/{character_id}
```

**路径参数:**
- `character_id` (integer): 角色ID

**示例请求:**
```bash
curl -X GET "http://localhost:8002/api/characters/1"
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Diluc",
    "name_cn": "迪卢克",
    "element": "Pyro",
    "weapon_type": "Claymore",
    "rarity": 5,
    "region": "Mondstadt",
    "birthday": "04-30",
    "description": "黎明酒庄的现任主人，蒙德城的贵公子。",
    "description_cn": "黎明酒庄的现任主人，蒙德城的贵公子。",
    "stats": {
      "base_hp": 12981,
      "base_atk": 335,
      "base_def": 784
    },
    "skills": [
      {
        "name": "Tempered Sword",
        "name_cn": "淬炼之剑",
        "type": "Normal Attack",
        "description": "普通攻击"
      }
    ],
    "constellations": [],
    "recommended_weapons": [],
    "recommended_artifacts": []
  },
  "message": "成功获取角色详情"
}
```

### 创建角色

```http
POST /api/characters
```

**请求体:**
```json
{
  "name": "New Character",
  "name_cn": "新角色",
  "element": "Pyro",
  "weapon_type": "Sword",
  "rarity": 5,
  "region": "Mondstadt",
  "description": "A new character",
  "description_cn": "一个新角色"
}
```

### 更新角色

```http
PUT /api/characters/{character_id}
```

### 删除角色

```http
DELETE /api/characters/{character_id}
```

## ⚔️ 武器 API

### 获取武器列表

```http
GET /api/weapons?page=1&per_page=20
```

**查询参数:**
- `page`, `per_page`: 分页参数
- `weapon_type`: 武器类型筛选
- `rarity`: 稀有度筛选 (3, 4, 5)
- `search`: 搜索关键词

**示例:**
```bash
curl -X GET "http://localhost:8002/api/weapons?weapon_type=Sword&rarity=5"
```

### 获取武器详情

```http
GET /api/weapons/{weapon_id}
```

## 💎 圣遗物 API

### 获取圣遗物列表

```http
GET /api/artifacts?page=1&per_page=20
```

**查询参数:**
- `page`, `per_page`: 分页参数
- `max_rarity`: 最大稀有度筛选
- `search`: 搜索关键词

### 获取圣遗物详情

```http
GET /api/artifacts/{artifact_id}
```

## 💍 圣遗物套装 API

### 获取圣遗物套装列表

```http
GET /api/artifact-sets?page=1&per_page=20
```

**查询参数:**
- `page` (integer): 页码,默认 1
- `per_page` (integer): 每页数量,默认 20,最大 100
- `rarity` (integer): 稀有度筛选 (3, 4, 5)
- `search` (string): 搜索关键词(套装名称)

**示例请求:**
```bash
curl -X GET "http://localhost:8001/api/artifact-sets?rarity=5&page=1&per_page=10"
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "artifact_sets": [
      {
        "id": 1,
        "set_name": "逆飞的流星",
        "set_name_en": "Fragment of Harmonic Whimsy",
        "max_rarity": 5,
        "two_piece_bonus": "攻击力提高18%",
        "four_piece_bonus": "施放元素战技后的8秒内,攻击力提升25%..."
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 10,
      "total": 50,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  },
  "message": "成功获取10个圣遗物套装"
}
```

### 获取圣遗物套装详情

```http
GET /api/artifact-sets/{set_id}
```

**路径参数:**
- `set_id` (integer): 套装ID

**示例请求:**
```bash
curl -X GET "http://localhost:8001/api/artifact-sets/1"
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "set_name": "逆飞的流星",
    "set_name_en": "Fragment of Harmonic Whimsy",
    "max_rarity": 5,
    "two_piece_bonus": "攻击力提高18%",
    "four_piece_bonus": "施放元素战技后的8秒内,攻击力提升25%...",
    "source": "须弥「沙海守望台」秘境",
    "pieces": [
      {
        "piece_name": "流星的巨蛋",
        "piece_type": "Flower",
        "main_stat": "生命值",
        "icon_url": "..."
      }
    ]
  },
  "message": "成功获取圣遗物套装详情"
}
```

### 根据套装名称获取详情

```http
GET /api/artifact-sets/name/{set_name}
```

**路径参数:**
- `set_name` (string): 套装名称(中文或英文)

**示例:**
```bash
curl -X GET "http://localhost:8001/api/artifact-sets/name/逆飞的流星"
```

### 按稀有度获取套装列表

```http
GET /api/artifact-sets/rarity/{rarity}?limit=50
```

**路径参数:**
- `rarity` (integer): 稀有度 (3, 4, 5)

**查询参数:**
- `limit` (integer): 返回数量限制,默认 50

**示例:**
```bash
curl -X GET "http://localhost:8001/api/artifact-sets/rarity/5?limit=20"
```

### 搜索圣遗物套装

```http
GET /api/artifact-sets/search/?q=keyword&limit=20
```

**查询参数:**
- `q` (string, 必需): 搜索关键词
- `limit` (integer): 返回数量限制,默认 20

**示例:**
```bash
curl -X GET "http://localhost:8001/api/artifact-sets/search/?q=流星&limit=10"
```

### 获取套装统计信息

```http
GET /api/artifact-sets/stats/overview
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "total_artifact_sets": 50,
    "by_rarity": {
      "5": 38,
      "4": 9,
      "3": 3
    }
  },
  "message": "成功获取圣遗物套装统计信息"
}
```

## 👾 怪物 API

### 获取怪物列表

```http
GET /api/monsters?page=1&per_page=20
```

**查询参数:**
- `page`, `per_page`: 分页参数
- `monster_type`: 怪物类型筛选 (Common, Elite, Boss)
- `category`: 分类筛选
- `search`: 搜索关键词

### 获取怪物详情

```http
GET /api/monsters/{monster_id}
```

## 🔍 搜索 API

### 全局搜索

```http
GET /api/search?q=keyword&type=all
```

**查询参数:**
- `q` (string, 必需): 搜索关键词
- `type` (string): 搜索类型 (all, character, weapon, artifact, monster)
- `page`, `per_page`: 分页参数

**示例:**
```bash
curl -X GET "http://localhost:8001/api/search?q=Diluc&type=character"
```

## 🕷️ 爬虫 API

### 触发武器爬取

```http
POST /api/scrape/weapons
```

**说明:** 手动触发武器数据爬取任务

**示例请求:**
```bash
curl -X POST "http://localhost:8001/api/scrape/weapons"
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "scraped_count": 158,
    "created": 5,
    "updated": 153,
    "skipped": 0,
    "errors": 0
  },
  "message": "成功爬取158个武器数据"
}
```

### 触发圣遗物爬取

```http
POST /api/scrape/artifacts
```

**说明:** 手动触发圣遗物数据爬取任务

**示例:**
```bash
curl -X POST "http://localhost:8001/api/scrape/artifacts"
```

### 触发角色爬取

```http
POST /api/scrape/characters
```

**说明:** 手动触发角色数据爬取任务

**示例:**
```bash
curl -X POST "http://localhost:8001/api/scrape/characters"
```

### 获取爬虫状态

```http
GET /api/scrape/status
```

**说明:** 获取当前爬虫任务的执行状态

**示例响应:**
```json
{
  "success": true,
  "data": {
    "is_running": false,
    "last_run": "2025-11-13T10:30:00+08:00",
    "tasks": {
      "weapons": "completed",
      "artifacts": "completed",
      "characters": "idle"
    }
  }
}
```

## ⏰ 定时任务调度 API

### 获取调度器状态

```http
GET /api/scheduler/status
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "running": true,
    "status": "running"
  },
  "message": "调度器运行中"
}
```

### 设置默认定时任务

```http
POST /api/scheduler/setup/default
```

**说明:** 创建默认的每周定时爬取任务
- 角色数据：每周日凌晨 1:00
- 武器数据：每周日凌晨 2:00
- 圣遗物数据：每周日凌晨 3:00

**示例:**
```bash
curl -X POST "http://localhost:8001/api/scheduler/setup/default"
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "characters_weekly",
        "name": "角色数据定时爬取",
        "next_run_time": "2025-11-17T01:00:00+08:00",
        "trigger": "cron[month='*', day='*', day_of_week='0', hour='1', minute='0']",
        "pending": false
      },
      {
        "id": "weapons_weekly",
        "name": "武器数据定时爬取",
        "next_run_time": "2025-11-17T02:00:00+08:00",
        "trigger": "cron[month='*', day='*', day_of_week='0', hour='2', minute='0']",
        "pending": false
      },
      {
        "id": "artifacts_weekly",
        "name": "圣遗物数据定时爬取",
        "next_run_time": "2025-11-17T03:00:00+08:00",
        "trigger": "cron[month='*', day='*', day_of_week='0', hour='3', minute='0']",
        "pending": false
      }
    ],
    "total": 3
  },
  "message": "成功设置默认定时任务"
}
```

### 获取所有任务列表

```http
GET /api/scheduler/jobs
```

**示例响应:**
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "weapons_weekly",
        "name": "武器数据定时爬取",
        "next_run_time": "2025-11-17T02:00:00+08:00",
        "trigger": "cron[month='*', day='*', day_of_week='0', hour='2', minute='0']",
        "pending": false
      }
    ],
    "total": 1
  },
  "message": "成功获取1个任务"
}
```

### 创建新任务

```http
POST /api/scheduler/jobs
```

**请求体 (Cron调度):**
```json
{
  "job_type": "weapons",
  "schedule_type": "cron",
  "cron": "0 */6 * * *",
  "job_id": "weapons_6h"
}
```

**请求体 (间隔调度):**
```json
{
  "job_type": "artifacts",
  "schedule_type": "interval",
  "interval_hours": 12,
  "job_id": "artifacts_12h"
}
```

**任务类型 (job_type):**
- `characters` - 角色数据爬取
- `weapons` - 武器数据爬取
- `artifacts` - 圣遗物数据爬取
- `all` - 完整爬取（角色 + 武器 + 圣遗物）

**Cron表达式示例:**
```
0 2 * * *     # 每天凌晨2点
0 */6 * * *   # 每6小时执行一次
0 3 * * 0     # 每周日凌晨3点
0 4 1 * *     # 每月1号凌晨4点
0 9 * * 1-5   # 工作日早上9点
```

### 手动触发任务

```http
POST /api/scheduler/jobs/trigger
```

**请求体:**
```json
{
  "job_type": "weapons"
}
```

**说明:** 立即执行一次爬取任务，不影响定时任务的执行计划

**示例:**
```bash
curl -X POST "http://localhost:8001/api/scheduler/jobs/trigger" \
  -H "Content-Type: application/json" \
  -d '{"job_type": "characters"}'
```

### 获取任务详情

```http
GET /api/scheduler/jobs/{job_id}
```

### 暂停任务

```http
POST /api/scheduler/jobs/{job_id}/pause
```

### 恢复任务

```http
POST /api/scheduler/jobs/{job_id}/resume
```

### 删除任务

```http
DELETE /api/scheduler/jobs/{job_id}
```

### 查看执行历史

```http
GET /api/scheduler/history?limit=20
```

**查询参数:**
- `limit` (integer): 返回记录数量，默认 20，最大 100

**示例响应:**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "job_id": "scrape_weapons",
        "job_name": "武器数据爬取",
        "start_time": "2025-11-13T02:00:00+08:00",
        "end_time": "2025-11-13T02:05:32+08:00",
        "elapsed_seconds": 332.5,
        "status": "success",
        "stats": {
          "scraped_count": 158,
          "created": 5,
          "updated": 153,
          "skipped": 0,
          "errors": 0
        }
      }
    ],
    "total": 1
  },
  "message": "成功获取1条历史记录"
}
```

## 🏥 系统 API

### 健康检查

```http
GET /api/health
```

**响应:**
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T10:00:00Z",
  "service": "genshin-info-api"
}
```

### 详细健康检查

```http
GET /api/health/detailed
```

### API 版本信息

```http
GET /api/health/version
```

## 📊 错误处理

### 常见错误

**404 Not Found:**
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "角色不存在",
    "details": {
      "character_id": 999999
    }
  }
}
```

**422 Validation Error:**
```json
{
  "detail": [
    {
      "loc": ["body", "rarity"],
      "msg": "ensure this value is less than or equal to 5",
      "type": "value_error.number.not_le"
    }
  ]
}
```

## 🔧 最佳实践

### 1. 使用分页

总是使用合理的分页参数，避免一次性获取大量数据：
```
?page=1&per_page=20  # 推荐
```

### 2. 使用筛选减少数据量

优先使用筛选条件，而不是获取所有数据后再筛选：
```
?element=Pyro&rarity=5  # 推荐
```

### 3. 缓存响应

对于不常变化的数据（如角色信息），建议在客户端缓存。

### 4. 错误处理

总是处理可能的错误响应：
```javascript
try {
  const response = await fetch('/api/characters/1');
  if (!response.ok) {
    // 处理错误
  }
  const data = await response.json();
} catch (error) {
  // 处理网络错误
}
```

## 📚 代码示例

### JavaScript/TypeScript

```typescript
// 获取角色列表
async function getCharacters(page = 1, element = null) {
  const params = new URLSearchParams({
    page: page.toString(),
    per_page: '20'
  });

  if (element) {
    params.append('element', element);
  }

  const response = await fetch(
    `http://localhost:8002/api/characters?${params}`
  );

  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  const data = await response.json();
  return data.data.characters;
}

// 获取角色详情
async function getCharacterDetail(id) {
  const response = await fetch(
    `http://localhost:8002/api/characters/${id}`
  );
  return await response.json();
}
```

### Python

```python
import requests

# 获取角色列表
def get_characters(page=1, element=None):
    params = {
        'page': page,
        'per_page': 20
    }
    if element:
        params['element'] = element

    response = requests.get(
        'http://localhost:8002/api/characters',
        params=params
    )
    response.raise_for_status()
    return response.json()['data']['characters']

# 获取角色详情
def get_character_detail(character_id):
    response = requests.get(
        f'http://localhost:8002/api/characters/{character_id}'
    )
    response.raise_for_status()
    return response.json()['data']
```

## 🔗 相关链接

- **项目仓库**: https://github.com/lastdanger/genshin-wiki-infomation
- **问题反馈**: https://github.com/lastdanger/genshin-wiki-infomation/issues
- **API文档**: http://localhost:8001/api/docs
- **调度器文档**: [SCHEDULER.md](./SCHEDULER.md)
- **爬虫指南**: [SCRAPER_GUIDE.md](./SCRAPER_GUIDE.md)

---

最后更新: 2025-11-13
版本: v1.0.0
