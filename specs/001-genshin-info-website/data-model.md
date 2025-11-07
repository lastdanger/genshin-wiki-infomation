# Data Model: 原神游戏信息网站

## 数据模型概览

本文档定义原神游戏信息网站的核心数据实体、关系和验证规则。设计基于功能规格中的6个关键实体，支持高效查询和数据完整性。

## 核心实体

### 1. Character (角色)

**用途**: 存储角色基础信息、属性、技能数据

```sql
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,          -- 角色姓名（如"钟离"）
    name_en VARCHAR(100),                       -- 英文名（如"Zhongli"）
    element VARCHAR(20) NOT NULL,               -- 元素类型（Geo, Anemo等）
    weapon_type VARCHAR(30) NOT NULL,           -- 武器类型（Polearm, Bow等）
    rarity INTEGER NOT NULL CHECK (rarity IN (4, 5)), -- 星级
    region VARCHAR(50),                         -- 地区（Liyue, Mondstadt等）
    base_stats JSONB NOT NULL,                  -- 基础属性 {"hp": 15552, "atk": 251, "def": 738}
    ascension_stats JSONB,                      -- 突破属性 {"stat": "geo_dmg_bonus", "value": 0.288}
    description TEXT,                           -- 角色描述
    birthday DATE,                              -- 生日
    constellation_name VARCHAR(100),            -- 命座名称
    title VARCHAR(200),                         -- 称号
    affiliation VARCHAR(100),                   -- 所属组织
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    -- 索引
    INDEX idx_characters_element (element),
    INDEX idx_characters_weapon_type (weapon_type),
    INDEX idx_characters_rarity (rarity),
    -- 全文搜索索引
    INDEX idx_characters_search USING GIN (to_tsvector('chinese', name || ' ' || COALESCE(description, '')))
);
```

### 2. CharacterSkill (角色技能)

**用途**: 存储角色技能详细信息和数值

```sql
CREATE TABLE character_skills (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    skill_type VARCHAR(30) NOT NULL,            -- 'normal_attack', 'elemental_skill', 'elemental_burst'
    name VARCHAR(150) NOT NULL,                 -- 技能名称
    description TEXT NOT NULL,                  -- 技能描述
    scaling_data JSONB NOT NULL,                -- 技能数值 {"lv1": {"dmg": 45.6}, "lv10": {"dmg": 97.2}}
    multipliers JSONB,                          -- 倍率信息
    energy_cost INTEGER DEFAULT 0,              -- 能量消耗（仅大招）
    cooldown DECIMAL(4,1),                      -- 冷却时间（秒）
    skill_order INTEGER NOT NULL DEFAULT 1,    -- 显示顺序

    UNIQUE(character_id, skill_type, skill_order)
);
```

### 3. CharacterTalent (角色天赋)

**用途**: 存储天赋被动技能和命座效果

```sql
CREATE TABLE character_talents (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    talent_type VARCHAR(30) NOT NULL,           -- 'passive1', 'passive2', 'passive3', 'constellation'
    level_requirement INTEGER DEFAULT 1,       -- 解锁等级要求
    constellation_level INTEGER,               -- 命座等级（1-6，仅命座）
    name VARCHAR(150) NOT NULL,
    description TEXT NOT NULL,
    effect_data JSONB,                         -- 效果数据

    INDEX idx_talents_character_type (character_id, talent_type)
);
```

### 4. Weapon (武器)

**用途**: 存储武器基础信息、属性、特效

```sql
CREATE TABLE weapons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    weapon_type VARCHAR(30) NOT NULL,           -- Sword, Bow, Catalyst等
    rarity INTEGER NOT NULL CHECK (rarity IN (3, 4, 5)),
    base_attack INTEGER NOT NULL,              -- 基础攻击力
    secondary_stat VARCHAR(50),                -- 副属性类型
    secondary_value DECIMAL(8,4),              -- 副属性数值
    passive_name VARCHAR(150),                 -- 被动技能名称
    passive_description TEXT,                  -- 被动技能描述
    passive_stats JSONB,                       -- 被动效果数值
    obtain_source VARCHAR(100),                -- 获取途径
    description TEXT,
    lore TEXT,                                 -- 武器背景故事
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_weapons_type (weapon_type),
    INDEX idx_weapons_rarity (rarity),
    INDEX idx_weapons_search USING GIN (to_tsvector('chinese', name || ' ' || COALESCE(description, '')))
);
```

### 5. Artifact (圣遗物)

**用途**: 存储圣遗物套装信息、效果、词条

```sql
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    set_name VARCHAR(100) NOT NULL,            -- 套装名称
    set_name_en VARCHAR(100),
    rarity_range VARCHAR(20) DEFAULT '4-5★',   -- 星级范围
    two_piece_effect TEXT,                     -- 2件套效果
    four_piece_effect TEXT,                    -- 4件套效果
    domain_name VARCHAR(100),                  -- 副本名称
    domain_location VARCHAR(100),              -- 副本位置
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_artifacts_search USING GIN (to_tsvector('chinese', set_name || ' ' || COALESCE(two_piece_effect, '')))
);
```

### 6. ArtifactPiece (圣遗物部件)

**用途**: 存储圣遗物各部件信息和主词条

```sql
CREATE TABLE artifact_pieces (
    id SERIAL PRIMARY KEY,
    artifact_id INTEGER REFERENCES artifacts(id) ON DELETE CASCADE,
    piece_type VARCHAR(30) NOT NULL,           -- 'flower', 'plume', 'sands', 'goblet', 'circlet'
    piece_name VARCHAR(150) NOT NULL,          -- 部件名称
    main_stats JSONB NOT NULL,                 -- 主词条选项 ["hp", "atk", "def", "elemental_mastery"]
    description TEXT,

    UNIQUE(artifact_id, piece_type)
);
```

### 7. Monster (怪物)

**用途**: 存储怪物基础信息、技能、弱点

```sql
CREATE TABLE monsters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    name_en VARCHAR(100),
    monster_type VARCHAR(50) NOT NULL,         -- 怪物分类
    category VARCHAR(50),                      -- 大类（Elite, Boss等）
    level_range VARCHAR(20),                   -- 等级范围
    element VARCHAR(30),                       -- 怪物元素
    resistances JSONB,                         -- 抗性 {"pyro": 0.1, "hydro": 0.5}
    immunities JSONB,                          -- 免疫 ["freeze", "petrify"]
    hp_scaling JSONB,                          -- 血量缩放
    attack_patterns JSONB,                     -- 攻击模式
    weak_points TEXT,                          -- 弱点部位
    drops JSONB,                              -- 掉落物品
    locations JSONB,                          -- 出现地点
    description TEXT,
    strategy_tips TEXT,                       -- 攻略建议
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_monsters_type (monster_type),
    INDEX idx_monsters_category (category),
    INDEX idx_monsters_search USING GIN (to_tsvector('chinese', name || ' ' || COALESCE(description, '')))
);
```

### 8. GameMechanic (游戏机制)

**用途**: 存储游戏机制说明、公式、攻略

```sql
CREATE TABLE game_mechanics (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50) NOT NULL,             -- 'basic', 'advanced', 'combat', 'elemental'
    difficulty_level VARCHAR(20) NOT NULL,    -- 'beginner', 'intermediate', 'advanced'
    summary TEXT NOT NULL,                     -- 简短摘要
    content TEXT NOT NULL,                     -- 详细内容
    formulas JSONB,                           -- 相关公式
    examples JSONB,                           -- 示例数据
    related_entities JSONB,                   -- 关联实体 {"characters": ["Zhongli"], "weapons": ["Staff of Homa"]}
    tags VARCHAR(500),                        -- 标签
    priority INTEGER DEFAULT 0,               -- 显示优先级
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_mechanics_category (category),
    INDEX idx_mechanics_difficulty (difficulty_level),
    INDEX idx_mechanics_search USING GIN (to_tsvector('chinese', title || ' ' || summary || ' ' || content))
);
```

### 9. Image (图片)

**用途**: 存储图片元数据、关联实体、审核状态

```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_path VARCHAR(500) NOT NULL,           -- 存储路径
    cdn_url VARCHAR(500),                      -- CDN访问URL
    image_type VARCHAR(50) NOT NULL,           -- 'official', 'user_upload', 'icon', 'splash'
    mime_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,                -- 文件大小（字节）
    width INTEGER,
    height INTEGER,

    -- 关联实体（多态关联）
    entity_type VARCHAR(50),                   -- 'character', 'weapon', 'artifact', 'monster'
    entity_id INTEGER,                         -- 关联实体ID

    -- 审核相关
    moderation_status VARCHAR(20) DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    moderated_by INTEGER,                      -- 审核员ID
    moderated_at TIMESTAMP,
    rejection_reason TEXT,

    -- 用户上传相关
    uploaded_by_ip INET,                       -- 上传IP（匿名系统）
    upload_session VARCHAR(100),               -- 会话标识

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_images_entity (entity_type, entity_id),
    INDEX idx_images_status (moderation_status),
    INDEX idx_images_type (image_type)
);
```

## 关联表

### 10. CharacterWeaponRecommendation (角色武器推荐)

**用途**: 存储角色与武器的推荐搭配关系

```sql
CREATE TABLE character_weapon_recommendations (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    weapon_id INTEGER REFERENCES weapons(id) ON DELETE CASCADE,
    recommendation_level VARCHAR(20) NOT NULL,  -- 'best', 'good', 'decent'
    reasoning TEXT NOT NULL,                    -- 推荐理由
    synergy_score DECIMAL(3,1),                -- 协同评分(1.0-10.0)
    notes TEXT,                                -- 额外说明
    created_at TIMESTAMP DEFAULT NOW(),

    UNIQUE(character_id, weapon_id),
    INDEX idx_char_weapon_level (character_id, recommendation_level)
);
```

### 11. CharacterArtifactRecommendation (角色圣遗物推荐)

**用途**: 存储角色与圣遗物的推荐搭配关系

```sql
CREATE TABLE character_artifact_recommendations (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    artifact_id INTEGER REFERENCES artifacts(id) ON DELETE CASCADE,
    recommendation_type VARCHAR(30) NOT NULL,   -- 'main_dps', 'support', 'burst_dps'
    priority INTEGER NOT NULL DEFAULT 1,       -- 推荐优先级
    main_stats_recommendation JSONB NOT NULL,  -- 主词条推荐 {"sands": ["atk%", "hp%"], "goblet": ["geo_dmg", "hp%"]}
    sub_stats_priority JSONB,                  -- 副词条优先级 ["crit_rate", "crit_dmg", "hp%"]
    set_combination VARCHAR(100),              -- 套装组合（如"4pc"或"2pc+2pc"）
    reasoning TEXT NOT NULL,

    UNIQUE(character_id, artifact_id, recommendation_type),
    INDEX idx_char_artifact_type (character_id, recommendation_type)
);
```

## 数据验证规则

### 字符串长度限制
- 名称字段: 1-100字符
- 描述字段: 最大5000字符
- URL字段: 最大500字符

### 枚举值验证
- **元素类型**: Anemo, Geo, Electro, Dendro, Hydro, Pyro, Cryo
- **武器类型**: Sword, Bow, Catalyst, Claymore, Polearm
- **星级**: 3, 4, 5 (武器), 4, 5 (角色)
- **审核状态**: pending, approved, rejected

### JSONB字段结构

**角色基础属性** (base_stats):
```json
{
    "hp": 15552,
    "atk": 251,
    "def": 738
}
```

**技能数值** (scaling_data):
```json
{
    "lv1": {"dmg_multiplier": 45.6, "shield_hp": 1232},
    "lv9": {"dmg_multiplier": 97.2, "shield_hp": 2712}
}
```

**圣遗物主词条推荐** (main_stats_recommendation):
```json
{
    "flower": ["hp"],
    "plume": ["atk"],
    "sands": ["hp%", "atk%", "def%"],
    "goblet": ["geo_dmg", "hp%"],
    "circlet": ["crit_rate", "crit_dmg", "hp%"]
}
```

## 数据状态转换

### 图片审核流程
1. `pending` → `approved` (通过审核)
2. `pending` → `rejected` (拒绝，记录原因)
3. `rejected` → `pending` (重新提交)

### 数据同步状态
- 每个实体表包含 `updated_at` 时间戳
- 同步脚本使用时间戳进行增量更新
- 冲突解决：外部数据优先，保留用户生成内容

## 性能优化

### 索引策略
1. **主键索引**: 所有表自动创建
2. **外键索引**: 关联字段自动索引
3. **查询索引**: 按元素、武器类型、星级等常用筛选条件
4. **全文搜索索引**: GIN索引支持中文分词
5. **复合索引**: (character_id, recommendation_level) 等高频查询组合

### 查询优化
1. **物化视图**: 复杂统计查询（角色武器推荐统计）
2. **部分索引**: 仅索引 `moderation_status = 'approved'` 的图片
3. **JSONB GIN索引**: 优化技能数值、属性等JSON字段查询

### 缓存策略
1. **Redis缓存**: 热门角色/武器列表，TTL 1小时
2. **应用层缓存**: 游戏机制等静态内容，TTL 24小时
3. **CDN缓存**: 图片和静态资源，长期缓存

## 数据迁移和备份

### 初始数据导入
1. 从哔哩哔哩wiki爬取基础数据
2. 从玉衡杯数据库同步数值数据
3. 官方资源图片批量导入

### 备份策略
- 日备份: pg_dump全量备份，压缩后上传云存储
- 实时备份: WAL-E流式备份到S3/OSS
- 恢复测试: 月度恢复演练

### 版本控制
- 结构变更: Alembic迁移脚本版本控制
- 数据变更: 记录变更历史，支持回滚

## 扩展性考虑

### 水平扩展
- 读写分离: 主库写入，从库查询
- 分片策略: 按地区（region）分片（未来考虑）

### 新功能支持
- 可扩展JSONB字段适应新游戏机制
- 预留entity_type支持未来新实体类型
- 灵活的推荐系统支持不同推荐算法