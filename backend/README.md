# 原神游戏信息网站 API

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green.svg)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

一个提供原神游戏角色、武器、圣遗物等全方位信息的 RESTful API 服务

[文档](#文档) •
[快速开始](#快速开始) •
[功能特性](#功能特性) •
[API端点](#api端点)

</div>

---

## 📖 项目简介

本项目是一个基于 FastAPI 构建的原神游戏信息 API 服务,提供以下功能:

- 🎭 **角色数据** - 完整的角色信息,包括技能、命之座、属性等
- ⚔️ **武器数据** - 武器属性、特效、推荐角色等
- 💎 **圣遗物数据** - 圣遗物套装效果、词条推荐
- 👾 **怪物数据** - 怪物图鉴、弱点、掉落物
- 🔍 **智能搜索** - 跨模块的全文搜索
- 🕷️ **自动爬虫** - 自动从Wiki爬取最新游戏数据
- ⏰ **定时任务** - 定时自动更新数据
- 📊 **缓存加速** - Redis缓存提升性能

## ✨ 功能特性

### 核心功能

- ⚡ **高性能** - 基于 FastAPI 的异步架构
- 🔄 **自动更新** - 定时任务自动爬取最新数据
- 📦 **完整数据** - 支持158个武器、50个圣遗物套装、18+角色
- 🔍 **强大搜索** - 支持模糊搜索和精确搜索
- 📄 **分页支持** - 所有列表接口支持分页
- 🛡️ **错误处理** - 完善的错误处理机制
- 📝 **API文档** - 自动生成的交互式API文档

### 技术架构

- **Web框架**: FastAPI 0.104.1
- **数据库**: PostgreSQL 14+ (支持JSONB)
- **ORM**: SQLAlchemy 2.0 (异步)
- **缓存**: Redis 5.0
- **爬虫**: BeautifulSoup4 + aiohttp
- **任务调度**: APScheduler 3.10.4
- **日志**: structlog

## 🚀 快速开始

### 前置要求

- Python 3.11+
- PostgreSQL 14+
- Redis 5.0+

### 安装步骤

1. **克隆项目**

```bash
git clone https://github.com/lastdanger/genshin-wiki-infomation.git
cd genshin-wiki-infomation/backend
```

2. **安装依赖**

```bash
pip install -r requirements.txt
```

3. **配置环境变量**

创建 `.env` 文件:

```env
# 数据库配置
DATABASE_URL=postgresql+asyncpg://user:password@localhost/genshin_db

# Redis配置
REDIS_URL=redis://localhost:6379/0

# 服务配置
ENVIRONMENT=development
DEBUG=True
```

4. **初始化数据库**

```bash
# 创建数据库表
python -m alembic upgrade head
```

5. **运行服务**

```bash
# 开发模式
uvicorn src.main:app --reload --port 8001

# 生产模式
uvicorn src.main:app --host 0.0.0.0 --port 8001 --workers 4
```

6. **访问API文档**

打开浏览器访问: http://localhost:8001/api/docs

### 初始化数据

首次运行需要爬取数据:

```bash
# 方式1: 使用爬虫脚本
python run_full_scrape.py

# 方式2: 通过API触发
curl -X POST "http://localhost:8001/api/scrape/weapons"
curl -X POST "http://localhost:8001/api/scrape/artifacts"
curl -X POST "http://localhost:8001/api/scrape/characters"

# 方式3: 设置定时任务(每周自动更新)
curl -X POST "http://localhost:8001/api/scheduler/setup/default"
```

## 📚 文档

### API文档

- **Swagger UI**: http://localhost:8001/api/docs
- **ReDoc**: http://localhost:8001/api/redoc
- **OpenAPI JSON**: http://localhost:8001/api/openapi.json

### 详细文档

- [API使用指南](./docs/API_USAGE_GUIDE.md) - 完整的API使用说明
- [API示例](./docs/API_EXAMPLES.md) - 实际使用示例
- [爬虫指南](./docs/SCRAPER_GUIDE.md) - 爬虫使用说明
- [调度器文档](./docs/SCHEDULER.md) - 定时任务配置
- [缓存策略](./docs/CACHING_STRATEGY.md) - 缓存使用说明
- [错误处理](./docs/ERROR_HANDLING.md) - 错误码说明

## 🔌 API端点

### 角色 API

```
GET    /api/characters              # 获取角色列表
GET    /api/characters/{id}          # 获取角色详情
GET    /api/characters/name/{name}   # 根据名称获取
GET    /api/characters/element/{element}  # 按元素筛选
POST   /api/characters              # 创建角色
PUT    /api/characters/{id}          # 更新角色
DELETE /api/characters/{id}          # 删除角色
```

### 武器 API

```
GET    /api/weapons                 # 获取武器列表
GET    /api/weapons/{id}             # 获取武器详情
GET    /api/weapons/name/{name}      # 根据名称获取
GET    /api/weapons/type/{type}      # 按类型筛选
GET    /api/weapons/search/          # 搜索武器
```

### 圣遗物套装 API

```
GET    /api/artifact-sets           # 获取套装列表
GET    /api/artifact-sets/{id}       # 获取套装详情
GET    /api/artifact-sets/name/{name}  # 根据名称获取
GET    /api/artifact-sets/rarity/{rarity}  # 按稀有度筛选
GET    /api/artifact-sets/search/    # 搜索套装
GET    /api/artifact-sets/stats/overview  # 获取统计信息
```

### 爬虫 API

```
POST   /api/scrape/weapons          # 爬取武器数据
POST   /api/scrape/artifacts        # 爬取圣遗物数据
POST   /api/scrape/characters       # 爬取角色数据
GET    /api/scrape/status           # 获取爬虫状态
```

### 调度器 API

```
GET    /api/scheduler/status        # 获取调度器状态
POST   /api/scheduler/setup/default # 设置默认任务
GET    /api/scheduler/jobs          # 获取任务列表
POST   /api/scheduler/jobs          # 创建任务
POST   /api/scheduler/jobs/trigger  # 手动触发任务
GET    /api/scheduler/history       # 查看执行历史
DELETE /api/scheduler/jobs/{id}     # 删除任务
```

### 搜索 API

```
GET    /api/search                  # 全局搜索
```

### 系统 API

```
GET    /api/health                  # 健康检查
GET    /api/health/detailed         # 详细健康检查
GET    /api/health/version          # 版本信息
```

## 🔧 配置说明

### 数据库配置

项目使用 PostgreSQL 作为主数据库,支持 JSONB 存储复杂数据结构。

```python
DATABASE_URL=postgresql+asyncpg://user:password@localhost/genshin_db
```

### 定时任务配置

默认定时任务配置(每周日自动更新):

- 角色数据: 每周日凌晨 1:00
- 武器数据: 每周日凌晨 2:00
- 圣遗物数据: 每周日凌晨 3:00

可通过API自定义调度:

```bash
# 创建自定义任务(每6小时执行一次)
curl -X POST "http://localhost:8001/api/scheduler/jobs" \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "weapons",
    "schedule_type": "cron",
    "cron": "0 */6 * * *",
    "job_id": "weapons_6h"
  }'
```

### 缓存配置

使用 Redis 进行缓存:

- 列表查询: 缓存 5 分钟
- 详情查询: 缓存 1 小时
- 统计数据: 缓存 1 小时

## 📊 数据统计

当前支持的数据量:

| 数据类型 | 数量 | 完整度 |
|---------|------|-------|
| 武器 | 158 | 100% |
| 圣遗物套装 | 50 | 100% |
| 角色 | 18+ | 88.9% |

## 🛠️ 开发指南

### 项目结构

```
backend/
├── src/
│   ├── api/              # API路由
│   ├── models/           # 数据模型
│   ├── scrapers/         # 爬虫模块
│   ├── services/         # 业务逻辑
│   ├── db/               # 数据库配置
│   ├── middleware/       # 中间件
│   └── utils/            # 工具函数
├── config/               # 配置文件
├── docs/                 # 文档
├── tests/                # 测试
└── alembic/              # 数据库迁移
```

### 添加新的数据类型

1. 在 `src/models/` 创建数据模型
2. 在 `src/scrapers/` 创建爬虫类
3. 在 `src/api/` 创建API路由
4. 在 `src/services/scheduler_service.py` 添加定时任务

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_weapons.py

# 生成覆盖率报告
pytest --cov=src tests/
```

## 🤝 贡献指南

欢迎贡献代码! 请遵循以下步骤:

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2025-11-13)

- ✨ 初始版本发布
- ⚡ 支持武器、圣遗物、角色数据查询
- 🕷️ 完整的爬虫系统
- ⏰ 定时任务调度系统
- 📚 完整的API文档

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

## 🙏 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 优秀的Web框架
- [SQLAlchemy](https://www.sqlalchemy.org/) - 强大的ORM
- [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) - HTML解析库
- [原神Wiki](https://wiki.biligame.com/ys) - 数据来源

## 📮 联系方式

- 项目仓库: https://github.com/lastdanger/genshin-wiki-infomation
- 问题反馈: https://github.com/lastdanger/genshin-wiki-infomation/issues
- 邮箱: support@genshin-wiki.com

---

<div align="center">
Made with ❤️ for Genshin Impact Players
</div>
