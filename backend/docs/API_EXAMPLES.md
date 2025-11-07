# API 请求响应示例

完整的 API 请求和响应示例集合

## 角色 API 示例

### 1. 获取所有火系角色

**请求:**
```http
GET /api/characters?element=Pyro&rarity=5 HTTP/1.1
Host: localhost:8002
Accept: application/json
```

**响应:** (200 OK)
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
        "birthday": "04-30",
        "constellation": "Noctua",
        "title": "The Dark Side of Dawn",
        "title_cn": "暗夜英雄",
        "icon_url": "/images/characters/diluc_icon.png",
        "portrait_url": "/images/characters/diluc_portrait.png"
      },
      {
        "id": 15,
        "name": "Hu Tao",
        "name_cn": "胡桃",
        "element": "Pyro",
        "weapon_type": "Polearm",
        "rarity": 5,
        "region": "Liyue",
        "birthday": "07-15",
        "constellation": "Papilio Charontis",
        "title": "Fragrance in Thaw",
        "title_cn": "雪霁梅香",
        "icon_url": "/images/characters/hutao_icon.png",
        "portrait_url": "/images/characters/hutao_portrait.png"
      }
    ],
    "pagination": {
      "page": 1,
      "per_page": 20,
      "total": 2,
      "total_pages": 1,
      "has_next": false,
      "has_prev": false
    }
  },
  "message": "成功获取角色列表，共 2 个角色"
}
```

### 2. 获取角色完整详情

**请求:**
```http
GET /api/characters/1 HTTP/1.1
Host: localhost:8002
Accept: application/json
```

**响应:** (200 OK)
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
    "constellation": "Noctua",
    "title": "The Dark Side of Dawn",
    "title_cn": "暗夜英雄",
    "description": "The tycoon of a winery empire in Mondstadt, unmatched in every possible way.",
    "description_cn": "蒙德城的贵公子，黎明酒庄的现任主人，财力与实力俱备的贵族。",
    "affiliation": "Dawn Winery",
    "affiliation_cn": "黎明酒庄",
    "stats": {
      "base_hp": 12981,
      "base_atk": 335,
      "base_def": 784,
      "ascension_stat": "CRIT Rate",
      "ascension_value": 19.2
    },
    "skills": [
      {
        "id": 1,
        "name": "Tempered Sword",
        "name_cn": "淬炼之剑",
        "type": "Normal Attack",
        "description": "Normal Attack: Perform up to 4 consecutive strikes.",
        "description_cn": "普通攻击：进行至多四段的连续斩击。"
      },
      {
        "id": 2,
        "name": "Searing Onslaught",
        "name_cn": "逆焰之刃",
        "type": "Elemental Skill",
        "description": "Performs a forward slash that deals Pyro DMG.",
        "description_cn": "挥舞大剑向前斩出一道炎刃。"
      },
      {
        "id": 3,
        "name": "Dawn",
        "name_cn": "黎明",
        "type": "Elemental Burst",
        "description": "Releases intense flames to knock nearby enemies back.",
        "description_cn": "释放炽热的火焰。"
      }
    ],
    "talents": [
      {
        "name": "Relentless",
        "name_cn": "不灭的余烬",
        "type": "Passive",
        "description": "Diluc's Charged Attack Stamina Cost is decreased by 50%.",
        "description_cn": "重击的体力消耗降低50%。"
      }
    ],
    "constellations": [
      {
        "level": 1,
        "name": "Conviction",
        "name_cn": "罪业的断罪",
        "description": "Diluc deals 15% more DMG to enemies whose HP is above 50%.",
        "description_cn": "对生命值高于50%的敌人造成的伤害提升15%。"
      }
    ],
    "recommended_weapons": [
      {
        "weapon_id": 1,
        "weapon_name": "Wolf's Gravestone",
        "weapon_name_cn": "狼的末路",
        "recommendation": "Best in Slot",
        "reasoning": "Highest base ATK and ATK% substat"
      }
    ],
    "recommended_artifacts": [
      {
        "artifact_set_id": 1,
        "set_name": "Crimson Witch of Flames",
        "set_name_cn": "炽烈的炎之魔女",
        "pieces": 4,
        "main_stats": "ATK% / Pyro DMG / CRIT Rate",
        "sub_stats": "CRIT Rate, CRIT DMG, ATK%, Energy Recharge"
      }
    ]
  },
  "message": "成功获取角色详情"
}
```

### 3. 搜索角色

**请求:**
```http
GET /api/characters?search=Diluc HTTP/1.1
Host: localhost:8002
```

**响应:** (200 OK)
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
        "rarity": 5
      }
    ],
    "pagination": {
      "total": 1
    }
  }
}
```

### 4. 角色不存在错误

**请求:**
```http
GET /api/characters/999999 HTTP/1.1
```

**响应:** (404 Not Found)
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

### 5. 参数验证错误

**请求:**
```http
GET /api/characters?rarity=10 HTTP/1.1
```

**响应:** (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "type": "less_than_equal",
      "loc": ["query", "rarity"],
      "msg": "Input should be less than or equal to 5",
      "input": "10",
      "ctx": {
        "le": 5
      }
    }
  ]
}
```

## 武器 API 示例

### 获取武器列表

**请求:**
```http
GET /api/weapons?weapon_type=Sword&rarity=5 HTTP/1.1
```

**响应:** (200 OK)
```json
{
  "success": true,
  "data": {
    "weapons": [
      {
        "id": 1,
        "name": "Aquila Favonia",
        "name_cn": "风鹰剑",
        "weapon_type": "Sword",
        "rarity": 5,
        "base_attack": 48,
        "sub_stat_type": "Physical DMG Bonus",
        "sub_stat_value": 9.0,
        "passive_name": "Falcon's Defiance",
        "icon_url": "/images/weapons/aquila_favonia.png"
      }
    ],
    "pagination": {
      "total": 1
    }
  }
}
```

## 圣遗物 API 示例

### 获取圣遗物详情

**请求:**
```http
GET /api/artifacts/1 HTTP/1.1
```

**响应:** (200 OK)
```json
{
  "success": true,
  "data": {
    "id": 1,
    "set_name": "Gladiator's Finale",
    "set_name_cn": "角斗士的终幕礼",
    "max_rarity": 5,
    "two_piece_bonus": "ATK +18%",
    "four_piece_bonus": "If the wielder uses a Sword, Claymore or Polearm, increases their Normal Attack DMG by 35%.",
    "pieces": [
      {
        "type": "Flower",
        "name": "Gladiator's Nostalgia",
        "name_cn": "角斗士的留恋"
      },
      {
        "type": "Plume",
        "name": "Gladiator's Destiny",
        "name_cn": "角斗士的归宿"
      }
    ]
  }
}
```

## 怪物 API 示例

### 获取怪物列表

**请求:**
```http
GET /api/monsters?monster_type=Boss HTTP/1.1
```

**响应:** (200 OK)
```json
{
  "success": true,
  "data": {
    "monsters": [
      {
        "id": 1,
        "name": "Stormterror Dvalin",
        "name_cn": "风魔龙·特瓦林",
        "monster_type": "Boss",
        "category": "Weekly Boss",
        "description": "A massive dragon that once protected Mondstadt.",
        "weaknesses": ["Anemo", "Cryo"],
        "drops": ["Dvalin's Plume", "Dvalin's Claw"]
      }
    ]
  }
}
```

## 搜索 API 示例

### 全局搜索

**请求:**
```http
GET /api/search?q=pyro&type=all HTTP/1.1
```

**响应:** (200 OK)
```json
{
  "success": true,
  "data": {
    "characters": [
      {"id": 1, "name": "Diluc", "type": "character"},
      {"id": 15, "name": "Hu Tao", "type": "character"}
    ],
    "weapons": [],
    "artifacts": [
      {"id": 5, "name": "Crimson Witch of Flames", "type": "artifact"}
    ],
    "total_results": 3
  }
}
```

## 系统 API 示例

### 健康检查

**请求:**
```http
GET /api/health HTTP/1.1
```

**响应:** (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T10:30:00Z",
  "service": "genshin-info-api",
  "version": "1.0.0"
}
```

### 详细健康检查

**请求:**
```http
GET /api/health/detailed HTTP/1.1
```

**响应:** (200 OK)
```json
{
  "status": "healthy",
  "timestamp": "2025-11-07T10:30:00Z",
  "service": "genshin-info-api",
  "version": "1.0.0",
  "components": {
    "database": {
      "status": "healthy",
      "response_time_ms": 5.2
    },
    "cache": {
      "status": "healthy",
      "response_time_ms": 1.8
    }
  },
  "uptime_seconds": 3600
}
```

---

最后更新: 2025-11-07
