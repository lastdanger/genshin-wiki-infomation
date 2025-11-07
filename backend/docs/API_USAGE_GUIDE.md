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
curl -X GET "http://localhost:8002/api/search?q=Diluc&type=character"
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
- **API文档**: http://localhost:8002/api/docs

---

最后更新: 2025-11-07
版本: v1.0.0
