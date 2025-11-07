# Quickstart Guide: 原神游戏信息网站

## 项目概览

本指南帮助新团队成员快速理解和启动原神游戏信息网站项目。系统旨在为原神玩家提供统一的角色、武器、圣遗物等游戏信息查询平台。

## 核心功能

1. **角色信息查询** (P1): 角色属性、技能、天赋关系图
2. **武器信息查询** (P2): 武器属性、特效、搭配推荐
3. **圣遗物信息查询** (P2): 套装效果、词条搭配建议
4. **怪物信息查询** (P3): 怪物机制、弱点、应对策略
5. **角色图片管理** (P3): 官方图片展示、用户图片上传
6. **游戏机制说明** (P3): 基础和进阶攻略指南

## 技术架构

### 后端技术栈
- **语言**: Python 3.11+
- **框架**: FastAPI (高性能异步Web框架)
- **数据库**: PostgreSQL 15+ (JSONB支持、中文搜索)
- **ORM**: SQLAlchemy 2.0 (异步支持)
- **缓存**: Redis (热点数据缓存)
- **任务队列**: Celery (数据同步后台任务)

### 前端技术栈
- **框架**: 现代Web框架 (React/Vue/Angular)
- **移动端**: 响应式设计，移动端优先
- **CDN**: 图片和静态资源加速

### 数据来源
- [哔哩哔哩游戏Wiki](https://wiki.biligame.com/ys/首页) - 基础游戏数据
- [玉衡杯数据库](https://homdgcat.wiki/gi/char) - 详细数值数据
- 原神官方 - 图片和最新信息

## 开发环境搭建

### 1. 环境要求
```bash
# Python环境
Python 3.11+
PostgreSQL 15+
Redis 6.0+
Node.js 18+ (前端开发)
```

### 2. 后端环境搭建

```bash
# 1. 克隆项目
git clone <repository-url>
cd genshin_wiki_information

# 2. 创建Python虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 3. 安装后端依赖
cd backend
pip install -r requirements.txt

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库和Redis连接信息

# 5. 数据库初始化
# 安装PostgreSQL zhparser扩展（中文分词）
psql -U postgres -c "CREATE DATABASE genshin_wiki;"
psql -U postgres -d genshin_wiki -c "CREATE EXTENSION zhparser;"

# 6. 运行数据库迁移
alembic upgrade head

# 7. 启动开发服务器
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 前端环境搭建

```bash
# 1. 进入前端目录
cd frontend

# 2. 安装依赖
npm install

# 3. 配置API端点
cp .env.example .env.local
# 编辑 .env.local 设置后端API地址

# 4. 启动开发服务器
npm run dev
```

### 4. 数据初始化

```bash
# 1. 启动Redis和Celery Worker
redis-server
celery -A src.services.background_tasks worker --loglevel=info

# 2. 运行数据同步脚本
python scripts/sync_initial_data.py

# 3. 验证数据导入
curl http://localhost:8000/api/characters?limit=5
```

## 项目结构

```
genshin_wiki_information/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI应用入口
│   │   ├── config.py            # 配置文件
│   │   ├── models/              # SQLAlchemy数据模型
│   │   │   ├── character.py
│   │   │   ├── weapon.py
│   │   │   └── ...
│   │   ├── schemas/             # Pydantic响应模型
│   │   ├── api/                 # API路由
│   │   │   ├── characters.py
│   │   │   ├── weapons.py
│   │   │   └── ...
│   │   ├── services/            # 业务逻辑
│   │   │   ├── data_sync.py     # 数据同步服务
│   │   │   └── image_service.py # 图片处理服务
│   │   └── utils/               # 工具函数
│   ├── tests/                   # 测试文件
│   ├── requirements.txt         # Python依赖
│   └── alembic/                 # 数据库迁移
├── frontend/
│   ├── src/
│   │   ├── components/          # 可复用组件
│   │   ├── pages/               # 页面组件
│   │   ├── services/            # API调用
│   │   └── styles/              # 样式文件
│   ├── public/                  # 静态资源
│   └── package.json
├── shared/
│   ├── types/                   # 共享类型定义
│   └── schemas/                 # 数据模型Schema
└── specs/                       # 项目规范文档
    └── 001-genshin-info-website/
        ├── spec.md              # 功能规格
        ├── plan.md              # 实施计划
        ├── data-model.md        # 数据模型
        └── contracts/           # API合约
```

## 关键API端点

### 角色相关
```
GET  /api/characters              # 角色列表
GET  /api/characters/{id}         # 角色详情
GET  /api/characters/{id}/skills  # 角色技能
GET  /api/characters/search       # 搜索角色
```

### 武器相关
```
GET  /api/weapons                 # 武器列表
GET  /api/weapons/{id}            # 武器详情
GET  /api/weapons/compare         # 武器对比
```

### 图片相关
```
POST /api/images/upload           # 上传图片
GET  /api/images/{type}/{id}      # 获取实体图片
GET  /api/images/gallery          # 图片画廊
```

## 开发流程

### 1. 新功能开发

1. **需求分析**: 查看 `spec.md` 了解用户故事和验收标准
2. **设计审查**: 参考 `data-model.md` 和 API合约
3. **分支创建**: `git checkout -b feature/角色技能优化`
4. **开发实现**:
   - 后端: 创建API端点，编写测试
   - 前端: 实现UI组件，集成API
5. **测试验证**: 运行单元测试和集成测试
6. **代码评审**: 提交PR，至少2人评审
7. **部署上线**: 合并到主分支，自动部署

### 2. 数据同步开发

```python
# src/services/data_sync.py
async def sync_character_data():
    """同步角色数据示例"""
    async with aiohttp.ClientSession() as session:
        # 1. 从哔哩哔哩wiki获取基础数据
        bilibili_data = await fetch_bilibili_characters(session)

        # 2. 从玉衡杯数据库获取数值数据
        homdgcat_data = await fetch_homdgcat_characters(session)

        # 3. 合并数据并更新数据库
        merged_data = merge_character_sources(bilibili_data, homdgcat_data)
        await update_character_database(merged_data)
```

### 3. 图片上传开发

```python
# src/api/images.py
@router.post("/upload")
async def upload_image(
    file: UploadFile = File(...),
    entity_type: str = Form(...),
    entity_id: int = Form(...)
):
    # 1. 验证文件格式和大小
    # 2. 异步上传到云存储
    # 3. 生成缩略图
    # 4. 保存元数据到数据库
    # 5. 返回访问URL
```

## 性能优化策略

### 1. 数据库优化
- **索引**: 为常用查询字段建立索引
- **JSONB**: 使用GIN索引优化技能数据查询
- **分页**: 所有列表接口支持分页，默认50条/页
- **连接池**: SQLAlchemy连接池，pool_size=20

### 2. 缓存策略
- **Redis缓存**: 角色/武器列表缓存1小时
- **CDN缓存**: 图片和静态资源长期缓存
- **应用缓存**: 游戏机制等静态内容缓存24小时

### 3. 前端优化
- **懒加载**: 图片和非首屏内容延迟加载
- **代码分割**: 按路由拆分JavaScript包
- **响应式图片**: 多尺寸图片适配不同设备
- **Service Worker**: 离线缓存和后台同步

## 部署指南

### 1. 生产环境部署

```bash
# Docker部署示例
docker-compose up -d postgres redis
docker-compose up -d backend frontend
```

### 2. 监控和日志
- **应用监控**: Prometheus + Grafana
- **错误追踪**: Sentry集成
- **性能监控**: 响应时间、数据库查询时间
- **业务指标**: 用户查询量、搜索成功率

### 3. 备份策略
- **数据库备份**: 每日自动备份，7天保留期
- **图片备份**: 同步到多个云存储
- **配置备份**: Git版本控制

## 常见问题

### Q: 如何添加新的游戏实体类型？

1. 在 `src/models/` 创建新的数据模型
2. 添加Pydantic schema到 `src/schemas/`
3. 创建API路由到 `src/api/`
4. 更新数据同步脚本
5. 运行数据库迁移

### Q: 如何优化搜索性能？

1. 检查PostgreSQL全文搜索索引
2. 考虑添加Elasticsearch
3. 优化搜索查询SQL
4. 增加Redis缓存层

### Q: 如何处理数据源更新？

1. 监控数据源变化（RSS/API）
2. 使用Celery定时任务同步
3. 实现冲突解决策略
4. 保留变更历史记录

## 团队协作

### 代码规范
- **Python**: 遵循PEP 8，使用black格式化
- **JavaScript**: ESLint + Prettier
- **API设计**: RESTful规范，使用OpenAPI文档
- **Git**: 使用conventional commits格式

### 沟通渠道
- **技术讨论**: GitHub Issues和PR评论
- **设计决策**: 更新相关文档文件
- **紧急问题**: 直接联系项目负责人

## 下一步行动

1. **环境搭建**: 按照上述步骤搭建开发环境
2. **API测试**: 使用Postman或curl测试关键接口
3. **数据验证**: 确认数据同步脚本正常工作
4. **功能开发**: 根据优先级开始实现用户故事

更多详细信息请参考：
- [功能规格说明](./spec.md)
- [数据模型设计](./data-model.md)
- [API接口文档](./contracts/)
- [实施计划](./plan.md)