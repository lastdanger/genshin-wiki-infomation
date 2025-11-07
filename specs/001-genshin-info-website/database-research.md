# Database Selection Research: 原神游戏信息网站

**Research Date**: 2025-11-05
**Purpose**: 为原神游戏信息网站选择最合适的数据库解决方案

---

## 1. 需求分析总结

### 1.1 数据特征
- **实体类型**: 角色(Character)、武器(Weapon)、圣遗物(Artifact)、怪物(Monster)、游戏机制(GameMechanic)、图片(Image)
- **数据复杂度**:
  - 层级化数据：技能→天赋关系树、套装效果、元素反应链
  - 多对多关系：角色-武器推荐、圣遗物-角色适配
  - 半结构化数据：技能描述、特效说明(可能包含JSON格式的动态数值)
- **数据特点**:
  - 读多写少（90%读取，10%写入）
  - 主要写入来自数据同步任务（24小时周期）
  - 需存储图片元数据和文件路径
  - 包含中文文本和特殊字符（元素符号、游戏术语）

### 1.2 性能要求
- **并发支持**: 100并发用户
- **响应时间**: 搜索<1秒，页面加载<3秒
- **数据同步**: 24小时周期，非实时更新
- **扩展性**: 预期1000+活跃用户

### 1.3 功能要求
- **搜索功能**: 跨实体类型全文搜索（角色名、技能名、武器名等）
- **中文支持**: 分词、拼音搜索、繁简转换
- **图片管理**: 存储路径、元数据、审核状态
- **关联查询**: 角色→推荐武器→推荐圣遗物（多层关联）

---

## 2. 数据库方案对比

### 2.1 PostgreSQL (关系型数据库)

#### 优势
**JSON支持 (9/10)**:
- 原生支持JSON和JSONB数据类型
- JSONB提供高效索引和查询（GIN索引）
- 适合存储技能数值、特效参数等半结构化数据
```sql
-- 示例：存储角色技能数据
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    skills JSONB,  -- {"normal_attack": {"base_dmg": 45.6, "scaling": "ATK"}}
    attributes JSONB
);
CREATE INDEX idx_skills ON characters USING GIN (skills);
```

**全文搜索 (8/10)**:
- 内置全文搜索引擎 (tsvector, tsquery)
- 支持中文分词（需扩展zhparser或jieba）
- 可配置分词权重和排名算法
```sql
-- 中文全文搜索示例
CREATE INDEX idx_char_search ON characters
USING GIN (to_tsvector('zhcfg', name || ' ' || description));

SELECT * FROM characters
WHERE to_tsvector('zhcfg', name) @@ to_tsquery('zhcfg', '钟离');
```

**性能 (8/10)**:
- 读优化：物化视图、分区表
- 连接池支持（pgBouncer）
- 100并发完全可支持（配合适当索引）
- 查询计划优化器成熟

**Python集成 (10/10)**:
- psycopg2/psycopg3：最成熟的Python适配器
- SQLAlchemy ORM完整支持
- asyncpg：异步高性能驱动（FastAPI推荐）
```python
# FastAPI + asyncpg示例
from sqlalchemy.ext.asyncio import create_async_engine
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/genshin")
```

**中文处理 (7/10)**:
- UTF-8完全支持
- 需额外配置分词扩展（zhparser）
- 排序支持中文拼音（需自定义collation）

#### 劣势
- 全文搜索性能不如专业搜索引擎（Elasticsearch）
- 中文分词需要额外扩展
- 水平扩展较复杂（需要分片方案如Citus）

#### 适用场景
✅ 数据结构复杂，需要强ACID保证
✅ 需要复杂关联查询（角色→武器→圣遗物）
✅ 数据一致性要求高（如图片审核状态变更）

---

### 2.2 MySQL (关系型数据库)

#### 优势
**JSON支持 (7/10)**:
- MySQL 5.7+支持JSON数据类型
- JSON_EXTRACT、JSON_CONTAINS等函数
- 性能不如PostgreSQL的JSONB
```sql
-- MySQL JSON示例
CREATE TABLE weapons (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    effect JSON  -- {"base_atk": 608, "sub_stat": {"crit_rate": 33.1}}
);
SELECT * FROM weapons WHERE JSON_EXTRACT(effect, '$.base_atk') > 500;
```

**全文搜索 (6/10)**:
- InnoDB全文索引支持中文（MySQL 5.6+）
- ngram解析器（适合CJK语言）
- 功能比PostgreSQL弱，不支持复杂排名
```sql
-- MySQL中文全文搜索
CREATE FULLTEXT INDEX ft_name ON characters(name) WITH PARSER ngram;
SELECT * FROM characters WHERE MATCH(name) AGAINST('钟离' IN NATURAL LANGUAGE MODE);
```

**性能 (7/10)**:
- InnoDB引擎优化读写
- 查询缓存（8.0已移除）
- 主从复制简单，适合读写分离
- 100并发可支持

**Python集成 (9/10)**:
- MySQL Connector、PyMySQL
- SQLAlchemy完整支持
- aiomysql（异步驱动）

**中文处理 (8/10)**:
- UTF-8mb4完整支持（包括emoji）
- ngram分词器内置，无需额外插件
- 排序和比较支持中文

#### 劣势
- JSON性能不如PostgreSQL
- 全文搜索功能较弱，缺少高级排名算法
- 事务隔离级别默认为REPEATABLE READ（可能产生间隙锁）

#### 适用场景
✅ 团队熟悉MySQL生态
✅ 需要简单的主从复制架构
✅ 对JSON查询性能要求不极致

---

### 2.3 MongoDB (文档型数据库)

#### 优势
**JSON支持 (10/10)**:
- 原生文档存储，天然适合JSON数据
- 灵活的Schema设计，易于迭代
- 嵌套文档和数组支持
```javascript
// MongoDB示例：角色文档
{
  "_id": ObjectId("..."),
  "name": "钟离",
  "element": "Geo",
  "skills": [
    {
      "name": "普通攻击·岩雨",
      "type": "normal_attack",
      "damage": [
        {"level": 1, "value": 45.6},
        {"level": 2, "value": 49.1}
      ]
    }
  ],
  "recommended_weapons": [
    {"weapon_id": ObjectId("..."), "priority": 1}
  ]
}
```

**全文搜索 (5/10)**:
- Text Index支持中文
- 搜索功能较基础，无高级排名
- Atlas Search（云服务）功能更强，但需付费
```javascript
// MongoDB文本搜索
db.characters.createIndex({ name: "text", description: "text" }, { default_language: "chinese" });
db.characters.find({ $text: { $search: "钟离 护盾" } });
```

**性能 (7/10)**:
- 读性能优秀（单文档查询）
- 写入性能高（无需JOIN）
- 关联查询较慢（$lookup性能不如SQL JOIN）
- 水平扩展容易（分片Sharding）

**Python集成 (9/10)**:
- pymongo：官方驱动
- Motor：异步驱动（FastAPI兼容）
- ODM支持：Beanie、MongoEngine
```python
# FastAPI + Motor示例
from motor.motor_asyncio import AsyncIOMotorClient
client = AsyncIOMotorClient("mongodb://localhost:27017")
db = client.genshin_db
```

**中文处理 (9/10)**:
- UTF-8完全支持
- 文本索引自动分词（简单规则）
- 排序和比较支持中文

#### 劣势
- **关联查询弱**: 角色→武器→圣遗物需要多次查询或复杂的$lookup
- **事务支持晚**: 4.0+才支持多文档事务，性能损耗大
- **数据冗余**: 为提高性能需要反规范化设计（数据重复）
- **全文搜索弱**: 复杂搜索需集成Elasticsearch

#### 适用场景
✅ 数据结构频繁变化（游戏版本迭代快）
✅ 单实体查询为主，关联查询少
✅ 需要水平扩展（高并发场景）

---

## 3. 专业搜索方案：Elasticsearch

### 3.1 Elasticsearch特性

**全文搜索 (10/10)**:
- 专业级全文搜索引擎（基于Lucene）
- 中文分词器：IK Analyzer、jieba
- 高级功能：拼音搜索、模糊匹配、高亮显示、搜索建议
```json
// Elasticsearch中文搜索示例
PUT /characters
{
  "settings": {
    "analysis": {
      "analyzer": {
        "ik_smart_pinyin": {
          "type": "custom",
          "tokenizer": "ik_smart",
          "filter": ["pinyin"]
        }
      }
    }
  }
}

// 搜索"钟离"或"zhongli"都能找到
GET /characters/_search
{
  "query": {
    "multi_match": {
      "query": "zhongli",
      "fields": ["name", "name.pinyin"]
    }
  }
}
```

**性能 (9/10)**:
- 搜索响应时间毫秒级
- 分布式架构，易扩展
- 缓存机制优化热门搜索

**Python集成 (8/10)**:
- elasticsearch-py：官方客户端
- elasticsearch-dsl：高级查询DSL
- 需要维护数据同步（主库→ES）

**中文处理 (10/10)**:
- IK分词器支持细粒度分词
- 拼音搜索插件（pinyin analyzer）
- 繁简转换支持

### 3.2 集成方案

**推荐架构**：主数据库 + Elasticsearch
```
PostgreSQL/MySQL (主数据库)
    ↓ 数据同步（Logstash/Python脚本）
Elasticsearch (搜索引擎)
```

**数据同步策略**:
1. **实时同步**: 使用Logstash JDBC输入插件（每分钟轮询）
2. **异步同步**: Python脚本在数据更新后推送到ES（使用消息队列）
3. **定时全量同步**: 每天凌晨全量重建索引（防止数据漂移）

**优势**:
- 主库保证数据一致性
- ES专注搜索性能
- 解耦存储和搜索

**劣势**:
- 增加系统复杂度
- 需维护两套数据
- 运维成本高（需要监控ES健康状态）

---

## 4. 方案推荐

### 4.1 推荐方案：PostgreSQL + Elasticsearch (可选)

#### 阶段1：初期（MVP阶段）
**选择**: **PostgreSQL单独使用**

**理由**:
1. **数据复杂度**: 角色-武器-圣遗物有复杂关联关系，关系型数据库更适合
2. **ACID保证**: 图片审核状态、用户上传记录需要强一致性
3. **JSON灵活性**: JSONB满足技能数值等半结构化数据存储
4. **中文搜索**: 通过zhparser扩展可满足基本搜索需求（100并发压力不大）
5. **Python生态**: psycopg3/asyncpg成熟度高，FastAPI集成简单
6. **运维成本**: 单数据库降低初期维护成本

**性能优化策略**:
```sql
-- 1. 为搜索字段创建GIN索引
CREATE INDEX idx_char_fulltext ON characters
USING GIN (to_tsvector('zhcfg', name || ' ' || description));

-- 2. 为关联查询创建外键索引
CREATE INDEX idx_weapon_char ON character_weapons(character_id);
CREATE INDEX idx_artifact_char ON character_artifacts(character_id);

-- 3. 物化视图缓存复杂查询
CREATE MATERIALIZED VIEW character_full_info AS
SELECT c.*, w.name as weapon_name, a.name as artifact_name
FROM characters c
LEFT JOIN weapons w ON c.recommended_weapon_id = w.id
LEFT JOIN artifacts a ON c.recommended_artifact_id = a.id;
```

**预期性能**:
- 简单查询（按ID）: <10ms
- 关联查询（角色+武器+圣遗物）: 50-100ms
- 全文搜索: 100-300ms（可通过索引优化到<100ms）
- 100并发: CPU使用率<50%（假设4核服务器）

#### 阶段2：扩展阶段（用户增长到5000+）
**升级**: **PostgreSQL + Elasticsearch**

**触发条件**:
- 搜索请求占总流量>30%
- PostgreSQL全文搜索响应时间>500ms
- 需要高级搜索功能（拼音搜索、搜索建议、typo容错）

**架构演进**:
```
                  ┌──────────────┐
                  │   FastAPI    │
                  └──────┬───────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    写入操作        关联查询         搜索请求
         │               │               │
         ▼               ▼               │
  ┌─────────────┐ ┌─────────────┐      │
  │ PostgreSQL  │ │ PostgreSQL  │      │
  │   (主库)    │ │  (从库-可选) │      │
  └──────┬──────┘ └─────────────┘      │
         │                              │
         │ 数据同步                      │
         ▼                              ▼
  ┌─────────────┐              ┌──────────────┐
  │  Logstash   │─────────────▶│Elasticsearch │
  └─────────────┘              └──────────────┘
```

**同步策略**:
```python
# Python脚本示例：增量同步到ES
from elasticsearch import AsyncElasticsearch
import asyncpg

async def sync_character_to_es(character_id):
    # 从PostgreSQL读取完整数据
    async with asyncpg.create_pool(DATABASE_URL) as pool:
        char = await pool.fetchrow("""
            SELECT c.*,
                   json_agg(w.*) as weapons,
                   json_agg(a.*) as artifacts
            FROM characters c
            LEFT JOIN character_weapons cw ON c.id = cw.character_id
            LEFT JOIN weapons w ON cw.weapon_id = w.id
            LEFT JOIN character_artifacts ca ON c.id = ca.character_id
            LEFT JOIN artifacts a ON ca.artifact_id = a.id
            WHERE c.id = $1
            GROUP BY c.id
        """, character_id)

    # 推送到Elasticsearch
    es = AsyncElasticsearch(['http://localhost:9200'])
    await es.index(index='characters', id=character_id, document=dict(char))
```

### 4.2 不推荐方案及原因

#### ❌ MongoDB单独使用
**不推荐理由**:
1. **关联查询复杂**: 角色→武器→圣遗物的推荐链需要多次查询或复杂$lookup
2. **数据冗余**: 需要在角色文档中嵌入武器信息，导致数据重复
3. **事务需求**: 图片审核+角色数据更新需要事务，MongoDB事务性能差
4. **团队不熟悉**: 如果团队主要使用SQL，学习曲线增加开发时间

**可能适用场景**:
- 如果需求改为"每个角色是独立的游戏数据包，很少关联查询"
- 或者"游戏数据结构每周都在大幅变化"

#### ❌ MySQL单独使用
**相比PostgreSQL的劣势**:
1. JSON查询性能低30-50%（JSONB vs JSON）
2. 全文搜索功能较弱，无法自定义排名算法
3. 缺少物化视图（需要手动维护汇总表）
4. 窗口函数支持较晚（8.0才支持）

**可用场景**:
- 团队已有MySQL运维经验，不想切换
- 与现有MySQL系统集成

---

## 5. Schema设计建议

### 5.1 PostgreSQL Schema设计

#### 核心表结构
```sql
-- 角色表
CREATE TABLE characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    name_en VARCHAR(100),  -- 英文名用于URL
    element VARCHAR(20) NOT NULL,  -- Pyro, Hydro, Electro等
    weapon_type VARCHAR(20) NOT NULL,  -- Sword, Claymore等
    rarity INTEGER CHECK (rarity IN (4, 5)),  -- 4星或5星
    base_attributes JSONB NOT NULL,  -- {"hp": 15552, "atk": 251, "def": 882}
    ascension_materials JSONB,  -- 突破材料列表
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 技能表（一对多关系）
CREATE TABLE character_skills (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    skill_type VARCHAR(20) NOT NULL,  -- normal_attack, elemental_skill等
    name VARCHAR(100) NOT NULL,
    description TEXT,
    scaling_data JSONB,  -- {"lv1": {"dmg": 45.6}, "lv2": {"dmg": 49.1}}
    cooldown DECIMAL,  -- 冷却时间（秒）
    energy_cost INTEGER,  -- 能量消耗
    sort_order INTEGER DEFAULT 0
);

-- 武器表
CREATE TABLE weapons (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    weapon_type VARCHAR(20) NOT NULL,
    rarity INTEGER CHECK (rarity IN (3, 4, 5)),
    base_atk INTEGER NOT NULL,
    sub_stat JSONB,  -- {"type": "CRIT Rate", "value": 33.1}
    passive_effect TEXT,  -- 武器特效描述
    passive_values JSONB,  -- 特效数值（精炼等级1-5）
    ascension_materials JSONB,
    lore TEXT,  -- 武器背景故事
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色武器推荐表（多对多）
CREATE TABLE character_weapon_recommendations (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    weapon_id INTEGER REFERENCES weapons(id) ON DELETE CASCADE,
    priority INTEGER DEFAULT 0,  -- 推荐优先级（1最高）
    notes TEXT,  -- 推荐理由
    UNIQUE(character_id, weapon_id)
);

-- 圣遗物表
CREATE TABLE artifacts (
    id SERIAL PRIMARY KEY,
    set_name VARCHAR(100) NOT NULL,
    set_bonus JSONB NOT NULL,  -- {"2pc": "ATK+18%", "4pc": "Normal Attack DMG+35%"}
    available_pieces JSONB,  -- ["Flower", "Plume", "Sands", "Goblet", "Circlet"]
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 角色圣遗物推荐表
CREATE TABLE character_artifact_recommendations (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    artifact_id INTEGER REFERENCES artifacts(id) ON DELETE CASCADE,
    main_stats JSONB,  -- {"Sands": ["ATK%", "ER%"], "Goblet": ["Geo DMG"]}
    sub_stats JSONB,  -- ["CRIT Rate", "CRIT DMG", "ATK%"]
    priority INTEGER DEFAULT 0,
    notes TEXT
);

-- 怪物表
CREATE TABLE monsters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),  -- Elite, Boss, Normal等
    family VARCHAR(50),  -- Hilichurl, Ruin Guard等
    level_range VARCHAR(20),  -- "1-100"
    resistances JSONB,  -- {"Pyro": 10, "Hydro": 10, "Electro": 10}
    weaknesses JSONB,  -- ["Pyro", "Cryo"]
    skills JSONB,  -- 技能列表
    drops JSONB,  -- 掉落物品
    locations TEXT[],  -- 出现地点
    tips TEXT  -- 应对策略
);

-- 图片表
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    entity_type VARCHAR(20) NOT NULL,  -- character, weapon, artifact等
    entity_id INTEGER NOT NULL,
    image_type VARCHAR(20),  -- icon, splash_art, gacha等
    file_path VARCHAR(500) NOT NULL,
    file_size INTEGER,
    mime_type VARCHAR(50),
    is_official BOOLEAN DEFAULT true,  -- 是否官方图片
    uploader_id INTEGER,  -- 用户上传（可选，如果有用户系统）
    moderation_status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 游戏机制表
CREATE TABLE game_mechanics (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    category VARCHAR(50),  -- basic, advanced
    content TEXT NOT NULL,
    formulas JSONB,  -- 计算公式
    examples JSONB,  -- 示例数据
    related_mechanics INTEGER[],  -- 关联机制ID
    sort_order INTEGER DEFAULT 0
);
```

#### 索引策略
```sql
-- 全文搜索索引
CREATE INDEX idx_characters_fulltext ON characters
USING GIN (to_tsvector('zhcfg', name || ' ' || COALESCE(description, '')));

CREATE INDEX idx_weapons_fulltext ON weapons
USING GIN (to_tsvector('zhcfg', name || ' ' || COALESCE(passive_effect, '')));

-- 外键索引（加速JOIN）
CREATE INDEX idx_char_skills_char_id ON character_skills(character_id);
CREATE INDEX idx_char_weapon_rec_char_id ON character_weapon_recommendations(character_id);
CREATE INDEX idx_char_weapon_rec_weapon_id ON character_weapon_recommendations(weapon_id);

-- 过滤查询索引
CREATE INDEX idx_characters_element ON characters(element);
CREATE INDEX idx_characters_weapon_type ON characters(weapon_type);
CREATE INDEX idx_weapons_type_rarity ON weapons(weapon_type, rarity);

-- JSONB索引（如果需要按JSON字段查询）
CREATE INDEX idx_characters_base_attrs ON characters USING GIN (base_attributes);
```

#### 物化视图（缓存复杂查询）
```sql
-- 角色完整信息视图
CREATE MATERIALIZED VIEW character_overview AS
SELECT
    c.id,
    c.name,
    c.element,
    c.weapon_type,
    c.rarity,
    c.base_attributes,
    json_agg(DISTINCT jsonb_build_object(
        'id', w.id,
        'name', w.name,
        'priority', cwr.priority
    )) FILTER (WHERE w.id IS NOT NULL) as recommended_weapons,
    json_agg(DISTINCT jsonb_build_object(
        'id', a.id,
        'name', a.set_name,
        'priority', car.priority
    )) FILTER (WHERE a.id IS NOT NULL) as recommended_artifacts,
    json_agg(DISTINCT jsonb_build_object(
        'id', cs.id,
        'name', cs.name,
        'type', cs.skill_type
    )) as skills
FROM characters c
LEFT JOIN character_weapon_recommendations cwr ON c.id = cwr.character_id
LEFT JOIN weapons w ON cwr.weapon_id = w.id
LEFT JOIN character_artifact_recommendations car ON c.id = car.character_id
LEFT JOIN artifacts a ON car.artifact_id = a.id
LEFT JOIN character_skills cs ON c.id = cs.character_id
GROUP BY c.id;

-- 创建索引
CREATE UNIQUE INDEX idx_char_overview_id ON character_overview(id);

-- 刷新策略（在数据同步后执行）
REFRESH MATERIALIZED VIEW CONCURRENTLY character_overview;
```

### 5.2 设计模式选择

#### 关系型模式 (推荐)
**优势**:
- 数据规范化，减少冗余
- 关联查询高效（JOIN性能好）
- 数据一致性有保障

**适用场景**:
- 角色、武器、圣遗物之间有明确关联关系
- 需要频繁的关联查询（如"这个武器适合哪些角色"）
- 数据更新频率低，一致性要求高

#### 文档型模式（不推荐）
**如果使用MongoDB，可能的设计**:
```javascript
// 角色文档（包含嵌入式子文档）
{
  "_id": ObjectId("..."),
  "name": "钟离",
  "element": "Geo",
  "skills": [  // 嵌入式数组
    {"name": "普通攻击", "type": "normal_attack", ...}
  ],
  "recommended_weapons": [  // 反规范化：直接嵌入武器信息
    {
      "weapon_id": ObjectId("..."),
      "name": "护摩之杖",  // 数据冗余
      "priority": 1
    }
  ]
}
```

**问题**:
- 武器信息更新时，需要同步更新所有角色文档
- 查询"哪些角色推荐这个武器"需要扫描所有角色文档（慢）

---

## 6. 搜索策略推荐

### 6.1 阶段1：PostgreSQL内置搜索

#### 实现方案
```sql
-- 1. 安装中文分词扩展
CREATE EXTENSION zhparser;
CREATE TEXT SEARCH CONFIGURATION zhcfg (PARSER = zhparser);
ALTER TEXT SEARCH CONFIGURATION zhcfg ADD MAPPING FOR n,v,a,i,e,l WITH simple;

-- 2. 创建搜索函数
CREATE OR REPLACE FUNCTION search_entities(search_term TEXT)
RETURNS TABLE(
    entity_type VARCHAR,
    entity_id INTEGER,
    name VARCHAR,
    description TEXT,
    rank REAL
) AS $$
BEGIN
    RETURN QUERY
    -- 搜索角色
    SELECT
        'character'::VARCHAR as entity_type,
        c.id as entity_id,
        c.name,
        c.description,
        ts_rank(to_tsvector('zhcfg', c.name || ' ' || COALESCE(c.description, '')),
                to_tsquery('zhcfg', search_term)) as rank
    FROM characters c
    WHERE to_tsvector('zhcfg', c.name || ' ' || COALESCE(c.description, ''))
          @@ to_tsquery('zhcfg', search_term)

    UNION ALL

    -- 搜索武器
    SELECT
        'weapon'::VARCHAR,
        w.id,
        w.name,
        w.passive_effect,
        ts_rank(to_tsvector('zhcfg', w.name || ' ' || COALESCE(w.passive_effect, '')),
                to_tsquery('zhcfg', search_term)) as rank
    FROM weapons w
    WHERE to_tsvector('zhcfg', w.name || ' ' || COALESCE(w.passive_effect, ''))
          @@ to_tsquery('zhcfg', search_term)

    UNION ALL

    -- 搜索圣遗物
    SELECT
        'artifact'::VARCHAR,
        a.id,
        a.set_name,
        a.set_bonus::TEXT,
        ts_rank(to_tsvector('zhcfg', a.set_name),
                to_tsquery('zhcfg', search_term)) as rank
    FROM artifacts a
    WHERE to_tsvector('zhcfg', a.set_name) @@ to_tsquery('zhcfg', search_term)

    ORDER BY rank DESC
    LIMIT 50;
END;
$$ LANGUAGE plpgsql;
```

#### FastAPI集成示例
```python
from fastapi import FastAPI, Query
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text

app = FastAPI()
engine = create_async_engine("postgresql+asyncpg://user:pass@localhost/genshin")

@app.get("/api/search")
async def search(q: str = Query(..., min_length=1)):
    async with AsyncSession(engine) as session:
        result = await session.execute(
            text("SELECT * FROM search_entities(:term)"),
            {"term": q}
        )
        rows = result.fetchall()
        return {
            "query": q,
            "results": [
                {
                    "type": row.entity_type,
                    "id": row.entity_id,
                    "name": row.name,
                    "description": row.description[:100],  # 截断
                    "relevance": float(row.rank)
                }
                for row in rows
            ]
        }
```

#### 性能优化
```python
# 1. 添加缓存（Redis）
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache

@app.get("/api/search")
@cache(expire=300)  # 缓存5分钟
async def search(q: str = Query(...)):
    # ... 搜索逻辑
    pass

# 2. 使用连接池
from sqlalchemy.pool import NullPool
engine = create_async_engine(
    "postgresql+asyncpg://user:pass@localhost/genshin",
    pool_size=20,  # 连接池大小
    max_overflow=10  # 超出连接池的最大连接数
)
```

### 6.2 阶段2：集成Elasticsearch

#### 索引映射定义
```json
PUT /genshin_entities
{
  "settings": {
    "analysis": {
      "analyzer": {
        "ik_pinyin": {
          "type": "custom",
          "tokenizer": "ik_max_word",
          "filter": ["lowercase", "pinyin"]
        }
      },
      "filter": {
        "pinyin": {
          "type": "pinyin",
          "keep_first_letter": true,
          "keep_separate_first_letter": false,
          "keep_full_pinyin": true,
          "keep_original": true,
          "limit_first_letter_length": 16
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "entity_type": {"type": "keyword"},
      "entity_id": {"type": "integer"},
      "name": {
        "type": "text",
        "analyzer": "ik_smart",
        "fields": {
          "pinyin": {
            "type": "text",
            "analyzer": "ik_pinyin"
          },
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "description": {
        "type": "text",
        "analyzer": "ik_max_word"
      },
      "element": {"type": "keyword"},
      "weapon_type": {"type": "keyword"},
      "rarity": {"type": "integer"},
      "tags": {"type": "keyword"},
      "created_at": {"type": "date"}
    }
  }
}
```

#### 高级搜索功能
```python
from elasticsearch import AsyncElasticsearch

es = AsyncElasticsearch(['http://localhost:9200'])

async def advanced_search(
    query: str,
    entity_types: List[str] = None,
    filters: dict = None,
    page: int = 1,
    page_size: int = 20
):
    # 构建查询
    must = [
        {
            "multi_match": {
                "query": query,
                "fields": ["name^3", "name.pinyin^2", "description"],
                "type": "best_fields",
                "fuzziness": "AUTO"  # 容错（typo）
            }
        }
    ]

    # 添加过滤条件
    filter_conditions = []
    if entity_types:
        filter_conditions.append({"terms": {"entity_type": entity_types}})
    if filters:
        if "element" in filters:
            filter_conditions.append({"term": {"element": filters["element"]}})
        if "rarity" in filters:
            filter_conditions.append({"term": {"rarity": filters["rarity"]}})

    # 执行搜索
    response = await es.search(
        index="genshin_entities",
        body={
            "query": {
                "bool": {
                    "must": must,
                    "filter": filter_conditions
                }
            },
            "highlight": {
                "fields": {
                    "name": {},
                    "description": {"fragment_size": 150}
                }
            },
            "from": (page - 1) * page_size,
            "size": page_size,
            "sort": [
                "_score",  # 相关性排序
                {"created_at": "desc"}  # 次要排序
            ]
        }
    )

    return {
        "total": response['hits']['total']['value'],
        "results": [
            {
                "type": hit['_source']['entity_type'],
                "id": hit['_source']['entity_id'],
                "name": hit['_source']['name'],
                "description": hit['_source']['description'],
                "score": hit['_score'],
                "highlight": hit.get('highlight', {})
            }
            for hit in response['hits']['hits']
        ]
    }

# FastAPI端点
@app.get("/api/search/advanced")
async def search_advanced(
    q: str,
    types: str = Query(None, description="逗号分隔：character,weapon"),
    element: str = None,
    rarity: int = None,
    page: int = 1
):
    entity_types = types.split(',') if types else None
    filters = {}
    if element:
        filters['element'] = element
    if rarity:
        filters['rarity'] = rarity

    results = await advanced_search(q, entity_types, filters, page)
    return results
```

#### 搜索建议（自动补全）
```json
PUT /genshin_suggestions
{
  "mappings": {
    "properties": {
      "name": {
        "type": "completion",
        "analyzer": "ik_smart"
      }
    }
  }
}
```

```python
async def get_suggestions(prefix: str, size: int = 5):
    response = await es.search(
        index="genshin_suggestions",
        body={
            "suggest": {
                "name_suggest": {
                    "prefix": prefix,
                    "completion": {
                        "field": "name",
                        "size": size,
                        "skip_duplicates": True
                    }
                }
            }
        }
    )

    suggestions = response['suggest']['name_suggest'][0]['options']
    return [opt['text'] for opt in suggestions]

@app.get("/api/search/suggest")
async def suggest(q: str = Query(..., min_length=1)):
    return {"suggestions": await get_suggestions(q)}
```

---

## 7. 迁移与备份策略

### 7.1 数据迁移计划

#### 初始数据导入
```python
# 从外部数据源（哔哩哔哩wiki、玉衡杯数据库）导入

import asyncio
import asyncpg
from typing import List, Dict

async def import_characters(data: List[Dict]):
    """批量导入角色数据"""
    conn = await asyncpg.connect('postgresql://user:pass@localhost/genshin')

    async with conn.transaction():
        # 批量插入角色
        await conn.executemany("""
            INSERT INTO characters (name, name_en, element, weapon_type, rarity, base_attributes)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (name_en) DO UPDATE
            SET element = EXCLUDED.element,
                base_attributes = EXCLUDED.base_attributes,
                updated_at = CURRENT_TIMESTAMP
        """, [(char['name'], char['name_en'], char['element'],
               char['weapon_type'], char['rarity'], char['attributes'])
              for char in data])

        # 插入技能数据
        for char in data:
            char_id = await conn.fetchval(
                "SELECT id FROM characters WHERE name_en = $1",
                char['name_en']
            )

            await conn.executemany("""
                INSERT INTO character_skills
                (character_id, skill_type, name, description, scaling_data)
                VALUES ($1, $2, $3, $4, $5)
                ON CONFLICT DO NOTHING
            """, [(char_id, skill['type'], skill['name'],
                   skill['desc'], skill['scaling'])
                  for skill in char['skills']])

    await conn.close()

# 使用示例
if __name__ == "__main__":
    # 从API获取数据
    characters_data = fetch_from_bilibili_wiki()
    asyncio.run(import_characters(characters_data))
```

#### 增量同步脚本
```python
# scheduled_sync.py - 定时同步脚本（使用APScheduler）

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import logging

logger = logging.getLogger(__name__)

async def sync_all_data():
    """24小时周期的全量同步"""
    try:
        logger.info("开始数据同步...")

        # 1. 同步角色数据
        characters = await fetch_characters_from_sources()
        await import_characters(characters)

        # 2. 同步武器数据
        weapons = await fetch_weapons_from_sources()
        await import_weapons(weapons)

        # 3. 同步圣遗物数据
        artifacts = await fetch_artifacts_from_sources()
        await import_artifacts(artifacts)

        # 4. 刷新物化视图
        await refresh_materialized_views()

        # 5. 如果使用ES，同步到ES
        if USE_ELASTICSEARCH:
            await sync_to_elasticsearch()

        logger.info("数据同步完成")

    except Exception as e:
        logger.error(f"数据同步失败: {str(e)}")
        # 发送告警通知

# 启动调度器
scheduler = AsyncIOScheduler()
scheduler.add_job(sync_all_data, 'cron', hour=3)  # 每天凌晨3点
scheduler.start()
```

### 7.2 备份策略

#### PostgreSQL备份方案

**1. 自动化备份脚本**
```bash
#!/bin/bash
# backup.sh - PostgreSQL备份脚本

BACKUP_DIR="/var/backups/genshin_db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
DB_NAME="genshin"
DB_USER="postgres"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 全量备份（使用pg_dump）
pg_dump -U $DB_USER -F c -b -v -f "$BACKUP_DIR/genshin_$TIMESTAMP.backup" $DB_NAME

# 压缩备份
gzip "$BACKUP_DIR/genshin_$TIMESTAMP.backup"

# 删除7天前的备份
find $BACKUP_DIR -name "*.backup.gz" -mtime +7 -delete

echo "备份完成: genshin_$TIMESTAMP.backup.gz"
```

**2. Cron定时任务**
```bash
# 添加到crontab
crontab -e

# 每天凌晨2点执行备份
0 2 * * * /path/to/backup.sh >> /var/log/genshin_backup.log 2>&1
```

**3. 恢复测试**
```bash
# 恢复数据库（测试环境）
pg_restore -U postgres -d genshin_test -v genshin_20251105_020000.backup
```

#### 云备份策略

**使用对象存储（如AWS S3、阿里云OSS）**
```python
# cloud_backup.py
import boto3
from datetime import datetime

s3 = boto3.client('s3')

def upload_backup_to_s3(local_file: str, bucket: str):
    """上传备份到S3"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    s3_key = f"backups/genshin_{timestamp}.backup.gz"

    s3.upload_file(
        local_file,
        bucket,
        s3_key,
        ExtraArgs={'StorageClass': 'GLACIER'}  # 使用冷存储降低成本
    )

    print(f"备份已上传到 s3://{bucket}/{s3_key}")

# 集成到备份脚本
upload_backup_to_s3("/var/backups/genshin_db/latest.backup.gz", "my-genshin-backups")
```

#### 灾难恢复预案

**RTO/RPO目标**:
- **RPO (恢复点目标)**: 24小时（最多丢失1天数据）
- **RTO (恢复时间目标)**: 4小时（4小时内恢复服务）

**恢复步骤**:
1. 从备份恢复数据库（1小时）
2. 验证数据完整性（30分钟）
3. 重新部署应用服务（1小时）
4. 运行数据同步脚本（1小时）
5. 测试核心功能（30分钟）

---

## 8. 性能基准测试计划

### 8.1 测试场景

#### 场景1：角色详情查询
```sql
-- 查询钟离的完整信息（含技能、推荐武器、推荐圣遗物）
EXPLAIN ANALYZE
SELECT
    c.*,
    json_agg(DISTINCT cs.*) as skills,
    json_agg(DISTINCT jsonb_build_object('weapon', w.*, 'priority', cwr.priority)) as weapons,
    json_agg(DISTINCT jsonb_build_object('artifact', a.*, 'priority', car.priority)) as artifacts
FROM characters c
LEFT JOIN character_skills cs ON c.id = cs.character_id
LEFT JOIN character_weapon_recommendations cwr ON c.id = cwr.character_id
LEFT JOIN weapons w ON cwr.weapon_id = w.id
LEFT JOIN character_artifact_recommendations car ON c.id = car.character_id
LEFT JOIN artifacts a ON car.artifact_id = a.id
WHERE c.name_en = 'zhongli'
GROUP BY c.id;
```

**目标**: <50ms

#### 场景2：全文搜索
```sql
EXPLAIN ANALYZE
SELECT * FROM search_entities('护盾');
```

**目标**: <200ms（PostgreSQL），<50ms（Elasticsearch）

#### 场景3：武器推荐查询
```sql
-- 查询适合钟离的所有武器
EXPLAIN ANALYZE
SELECT w.*, cwr.priority, cwr.notes
FROM weapons w
JOIN character_weapon_recommendations cwr ON w.id = cwr.weapon_id
JOIN characters c ON cwr.character_id = c.id
WHERE c.name_en = 'zhongli'
ORDER BY cwr.priority;
```

**目标**: <30ms

### 8.2 压力测试

使用Apache JMeter或Locust进行并发测试：

```python
# locustfile.py - 压力测试脚本
from locust import HttpUser, task, between

class GenshinUser(HttpUser):
    wait_time = between(1, 3)  # 用户操作间隔1-3秒

    @task(3)  # 权重3：最常见操作
    def view_character(self):
        characters = ['zhongli', 'raiden-shogun', 'hu-tao', 'ganyu']
        char = random.choice(characters)
        self.client.get(f"/api/characters/{char}")

    @task(2)  # 权重2
    def search(self):
        queries = ['护盾', '武器', '圣遗物', '雷电']
        q = random.choice(queries)
        self.client.get(f"/api/search?q={q}")

    @task(1)  # 权重1
    def list_weapons(self):
        self.client.get("/api/weapons")

# 运行：locust -f locustfile.py --host=http://localhost:8000
# 模拟100并发用户
```

**成功标准**:
- 95%请求响应时间<1秒
- 错误率<1%
- CPU使用率<70%
- 内存使用稳定（无泄漏）

---

## 9. 总结与行动计划

### 9.1 最终推荐

| 项目 | 推荐方案 | 理由 |
|------|---------|------|
| **主数据库** | **PostgreSQL 15+** | JSONB性能、全文搜索、ACID保证、Python生态成熟 |
| **搜索引擎** | **初期不用，后期加Elasticsearch** | MVP阶段PostgreSQL够用，用户增长后再加ES |
| **Schema设计** | **关系型（规范化）** | 数据关联复杂，JOIN性能好，一致性强 |
| **中文分词** | **zhparser扩展** | PostgreSQL原生支持，无需额外服务 |
| **缓存** | **Redis** | 缓存热门查询结果和搜索建议 |

### 9.2 实施路线图

#### 第1阶段（MVP - 1-2月）
- [ ] 安装PostgreSQL 15，配置zhparser扩展
- [ ] 设计并创建核心表结构（characters, weapons, artifacts等）
- [ ] 实现基础CRUD API（FastAPI + SQLAlchemy）
- [ ] 开发数据同步脚本（从外部数据源导入）
- [ ] 实现PostgreSQL全文搜索
- [ ] 配置自动化备份（cron + pg_dump）
- [ ] 性能基准测试（单机100并发）

**技术栈**:
- PostgreSQL 15 + zhparser
- Python 3.11 + FastAPI + asyncpg
- SQLAlchemy 2.0（异步ORM）
- APScheduler（定时任务）

#### 第2阶段（优化 - 3-4月）
- [ ] 添加Redis缓存层（缓存热门查询）
- [ ] 创建物化视图优化复杂查询
- [ ] 实现搜索结果高亮显示
- [ ] 配置主从复制（可选，如需读写分离）
- [ ] 监控告警（Prometheus + Grafana）
- [ ] 压力测试并优化慢查询

#### 第3阶段（扩展 - 5-6月，如需要）
- [ ] 评估是否需要Elasticsearch（基于搜索流量）
- [ ] 如需ES，配置Logstash同步数据
- [ ] 实现高级搜索功能（拼音、typo容错、搜索建议）
- [ ] A/B测试搜索性能（PostgreSQL vs Elasticsearch）
- [ ] 水平扩展（读副本或分片）

### 9.3 关键决策点

| 决策时机 | 评估指标 | 行动 |
|---------|---------|------|
| **MVP完成后** | 搜索请求占比<20% | 继续使用PostgreSQL搜索 |
| **用户增长到3000+** | 搜索请求占比>30% | 评估引入Elasticsearch |
| **搜索延迟>500ms** | 95分位响应时间 | 立即优化索引或加ES |
| **并发超过200** | CPU/内存使用率>80% | 添加读副本或升级硬件 |

### 9.4 风险与缓解

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| **PostgreSQL全文搜索性能不足** | 中 | 准备ES集成方案，快速切换 |
| **数据同步失败** | 高 | 实现重试机制+告警，保留上次成功数据 |
| **备份恢复测试未做** | 高 | 每月执行一次恢复演练 |
| **中文分词效果差** | 中 | 评估jieba分词或切换到ES+IK |
| **数据库单点故障** | 高 | 配置主从复制，定期故障切换演练 |

---

## 10. 参考资源

### 10.1 PostgreSQL资源
- **官方文档**: https://www.postgresql.org/docs/15/
- **zhparser扩展**: https://github.com/amutu/zhparser
- **全文搜索指南**: https://www.postgresql.org/docs/15/textsearch.html
- **JSONB性能优化**: https://www.postgresql.org/docs/15/datatype-json.html

### 10.2 Elasticsearch资源
- **IK分词器**: https://github.com/medcl/elasticsearch-analysis-ik
- **Pinyin插件**: https://github.com/medcl/elasticsearch-analysis-pinyin
- **Python客户端**: https://elasticsearch-py.readthedocs.io/

### 10.3 工具与库
- **FastAPI**: https://fastapi.tiangolo.com/
- **asyncpg**: https://magicstack.github.io/asyncpg/
- **SQLAlchemy 2.0**: https://docs.sqlalchemy.org/en/20/
- **APScheduler**: https://apscheduler.readthedocs.io/

### 10.4 最佳实践
- **12-Factor App**: https://12factor.net/zh_cn/
- **数据库索引优化**: https://use-the-index-luke.com/
- **API设计规范**: https://restfulapi.net/

---

**研究完成日期**: 2025-11-05
**下一步行动**: 等待用户确认方案后，开始第1阶段实施（创建数据库Schema）
