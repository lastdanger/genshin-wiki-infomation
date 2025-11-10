# 原神游戏信息网站 | Genshin Impact Wiki

<div align="center">

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![React](https://img.shields.io/badge/React-18.2-61DAFB)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-009688)](https://fastapi.tiangolo.com/)

一个功能完整的原神游戏信息全栈 Web 应用，提供角色、武器、圣遗物、怪物等详细资料查询。

[快速开始](#-快速开始) •
[功能特性](#-功能特性) •
[技术栈](#️-技术栈) •
[文档](#-文档) •
[贡献指南](#-贡献)

</div>

---

## 📖 目录

- [项目简介](#-项目简介)
- [快速开始](#-快速开始)
- [功能特性](#-功能特性)
- [技术栈](#️-技术栈)
- [项目结构](#-项目结构)
- [架构设计](#-架构设计)
- [文档](#-文档)
- [开发指南](#-开发指南)
- [部署](#-部署)
- [测试](#-测试)
- [贡献](#-贡献)
- [许可证](#-许可证)

---

## 🎮 项目简介

原神游戏信息网站是一个现代化的全栈 Web 应用，旨在为原神玩家提供：

- **完整的游戏资料库**：角色、武器、圣遗物、怪物等详细信息
- **智能搜索系统**：跨实体全局搜索，快速定位所需资料
- **数据可视化**：直观展示角色属性、武器对比等
- **响应式设计**：完美适配桌面端和移动端

### 🎯 设计目标

- **数据准确性**：来源官方和可信数据源
- **用户体验**：简洁直观的界面设计
- **性能优化**：快速加载和流畅交互
- **可维护性**：模块化架构和完善文档

---

## 🚀 快速开始

### 前置要求

确保已安装以下工具：

| 工具 | 版本要求 | 说明 |
|------|---------|------|
| Python | 3.8+ | 后端运行环境 |
| Node.js | 16+ | 前端构建工具 |
| PostgreSQL | 12+ | 数据库 |
| Redis | 6+ | 缓存服务（可选） |

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/lastdanger/genshin-wiki-infomation.git
cd genshin-wiki-infomation
```

#### 2. 配置数据库

```bash
# 创建 PostgreSQL 数据库
createdb genshin_wiki

# 或使用 psql
psql -U postgres
CREATE DATABASE genshin_wiki;
\q
```

#### 3. 启动后端

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 配置环境变量（可选）
cp .env.example .env
# 编辑 .env 文件设置数据库连接等

# 运行数据库迁移
alembic upgrade head

# 启动服务器
uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 4. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
PORT=3002 npm start
```

#### 5. 访问应用

- **前端应用**: http://localhost:3002
- **后端 API**: http://localhost:8001
- **API 文档**: http://localhost:8001/docs
- **ReDoc 文档**: http://localhost:8001/redoc

> **端口配置**: 详细端口说明请查看 [PORT_CONFIG.md](./PORT_CONFIG.md)

---

## ✨ 功能特性

### 🎭 角色系统
- ✅ 角色列表和详情页面
- ✅ 按元素、武器类型、稀有度筛选
- ✅ 角色技能和天赋详细说明
- ✅ 突破材料和天赋升级材料
- ✅ 命之座信息

### ⚔️ 武器系统
- ✅ 武器图鉴和详情
- ✅ 武器对比功能
- ✅ 根据角色推荐武器
- ✅ 精炼效果展示

### 💎 圣遗物系统
- ✅ 圣遗物套装列表
- ✅ 主属性和副属性详情
- ✅ 套装效果说明
- ✅ 角色圣遗物推荐

### 👾 怪物系统
- ✅ 怪物图鉴
- ✅ 怪物属性和抗性
- ✅ 掉落物品信息
- ✅ 分布位置

### 🔍 搜索功能
- ✅ 跨实体全局搜索
- ✅ 搜索建议和自动完成
- ✅ 搜索历史记录
- ✅ 高级筛选

### 🛡️ 系统特性
- ✅ **完善的错误处理**：前后端统一错误处理机制
- ✅ **Redis 缓存**：提升 API 响应速度
- ✅ **单元测试**：85%+ 测试覆盖率
- ✅ **响应式设计**：支持桌面和移动设备
- ✅ **API 文档**：自动生成的 Swagger/ReDoc 文档

---

## 🏗️ 技术栈

### 后端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| FastAPI | 0.104+ | Web 框架 |
| SQLAlchemy | 2.0+ | ORM |
| PostgreSQL | 12+ | 关系型数据库 |
| Redis | 6+ | 缓存服务 |
| Alembic | - | 数据库迁移 |
| Uvicorn | - | ASGI 服务器 |
| Pydantic | 2.0+ | 数据验证 |

### 前端技术

| 技术 | 版本 | 用途 |
|------|------|------|
| React | 18.2 | UI 框架 |
| React Router | 6.18 | 路由管理 |
| Axios | 1.6 | HTTP 客户端 |
| Jest | - | 单元测试 |
| React Testing Library | - | 组件测试 |

### 开发工具

- **代码规范**: ESLint, Prettier, Black
- **版本控制**: Git, GitHub
- **CI/CD**: GitHub Actions
- **容器化**: Docker, Docker Compose

---

## 📁 项目结构

```
genshin_wiki_information/
├── backend/                      # 后端服务
│   ├── src/
│   │   ├── main.py              # 应用入口
│   │   ├── config.py            # 配置管理
│   │   ├── models/              # 数据库模型
│   │   │   ├── character.py
│   │   │   ├── weapon.py
│   │   │   └── artifact.py
│   │   ├── api/                 # API 路由
│   │   │   ├── characters.py
│   │   │   ├── weapons.py
│   │   │   └── cache_stats.py
│   │   ├── services/            # 业务逻辑
│   │   ├── cache/               # 缓存管理
│   │   │   ├── redis_client.py
│   │   │   └── cache_manager.py
│   │   └── utils/               # 工具函数
│   ├── docs/                    # 后端文档
│   │   ├── API_USAGE_GUIDE.md
│   │   ├── API_EXAMPLES.md
│   │   ├── ERROR_HANDLING.md
│   │   ├── CACHING_STRATEGY.md
│   │   └── CACHING_EXAMPLES.md
│   ├── tests/                   # 后端测试
│   ├── requirements.txt         # Python 依赖
│   └── alembic/                 # 数据库迁移
│
├── frontend/                    # 前端应用
│   ├── src/
│   │   ├── components/         # React 组件
│   │   │   ├── ErrorBoundary/  # 错误边界
│   │   │   ├── UI/            # UI 组件
│   │   │   │   └── Toast/     # Toast 提示
│   │   │   ├── Character/     # 角色组件
│   │   │   ├── Weapon/        # 武器组件
│   │   │   └── Layout/        # 布局组件
│   │   ├── pages/             # 页面组件
│   │   │   ├── HomePage.jsx
│   │   │   ├── CharacterListPage.jsx
│   │   │   └── CharacterDetailPage.jsx
│   │   ├── services/          # API 服务
│   │   │   ├── base/          # 基础服务
│   │   │   │   ├── interceptors.ts
│   │   │   │   └── BaseAPIService.js
│   │   │   └── errors/        # 错误处理
│   │   │       ├── errorHandler.ts
│   │   │       └── ApiError.ts
│   │   ├── hooks/             # 自定义 Hooks
│   │   │   └── useErrorHandler.ts
│   │   └── App.jsx           # 应用入口
│   ├── docs/                  # 前端文档
│   │   └── ERROR_HANDLING.md
│   ├── package.json          # Node 依赖
│   └── .env                  # 环境配置
│
├── docs/                      # 项目文档
│   ├── DEPLOYMENT.md         # 部署指南
│   ├── DEVELOPMENT.md        # 开发指南
│   └── CONTRIBUTING.md       # 贡献指南
│
├── specs/                     # 规格文档
│   └── 001-genshin-info-website/
│       ├── spec.md           # 功能规格
│       ├── plan.md           # 实施计划
│       └── tasks.md          # 任务列表
│
├── CHANGELOG.md              # 更新日志
├── PORT_CONFIG.md            # 端口配置
└── README.md                 # 项目说明
```

---

## 🔧 架构设计

### 整体架构

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Browser   │─────▶│   Frontend  │─────▶│   Backend   │
│             │◀─────│   (React)   │◀─────│  (FastAPI)  │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                      │
                            │                      │
                            ▼                      ▼
                     ┌─────────────┐      ┌─────────────┐
                     │   CDN/S3    │      │ PostgreSQL  │
                     │   (Assets)  │      │   + Redis   │
                     └─────────────┘      └─────────────┘
```

### 后端架构

- **三层架构**：API 层 → Service 层 → Model 层
- **缓存策略**：Redis 缓存热点数据，5-30分钟 TTL
- **错误处理**：统一的错误处理中间件和错误响应格式
- **API 设计**：RESTful API，符合 OpenAPI 3.0 规范

### 前端架构

- **组件化**：可复用的 UI 组件库
- **状态管理**：React Hooks + Context API
- **错误边界**：多层错误捕获机制
- **性能优化**：代码分割、懒加载、缓存

详细架构说明请查看 [ARCHITECTURE.md](./docs/ARCHITECTURE.md)

---

## 📚 文档

### 核心文档

- [📘 API 使用指南](./backend/docs/API_USAGE_GUIDE.md) - API 接口详细说明
- [📗 API 示例](./backend/docs/API_EXAMPLES.md) - API 调用示例代码
- [📕 错误处理 (后端)](./backend/docs/ERROR_HANDLING.md) - 后端错误处理机制
- [📙 错误处理 (前端)](./frontend/docs/ERROR_HANDLING.md) - 前端错误处理机制
- [📔 缓存策略](./backend/docs/CACHING_STRATEGY.md) - Redis 缓存设计
- [📓 缓存示例](./backend/docs/CACHING_EXAMPLES.md) - 缓存使用示例

### 开发文档

- [🛠️ 开发指南](./docs/DEVELOPMENT.md) - 本地开发环境搭建
- [🚀 部署指南](./docs/DEPLOYMENT.md) - 生产环境部署说明
- [🤝 贡献指南](./docs/CONTRIBUTING.md) - 如何参与项目开发
- [📝 更新日志](./CHANGELOG.md) - 版本更新记录

### API 文档

- **Swagger UI**: http://localhost:8001/docs - 交互式 API 文档
- **ReDoc**: http://localhost:8001/redoc - 美观的 API 文档

---

## 💻 开发指南

### 后端开发

```bash
cd backend

# 激活虚拟环境
source venv/bin/activate

# 安装开发依赖
pip install -r requirements-dev.txt

# 运行测试
pytest

# 代码格式化
black src/
isort src/

# 创建数据库迁移
alembic revision --autogenerate -m "description"

# 应用迁移
alembic upgrade head

# 启动开发服务器（自动重载）
uvicorn src.main:app --reload --port 8001
```

### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm start

# 运行测试
npm test

# 运行测试并生成覆盖率报告
npm test -- --coverage

# 代码格式化
npm run format

# 代码检查
npm run lint

# 修复 lint 错误
npm run lint:fix

# 构建生产版本
npm run build
```

### 代码规范

- **后端**: 遵循 PEP 8 规范，使用 Black 格式化
- **前端**: 遵循 Airbnb JavaScript Style Guide
- **提交信息**: 遵循 Conventional Commits 规范

```
feat: 新功能
fix: 修复 bug
docs: 文档更新
style: 代码格式调整
refactor: 重构
test: 测试相关
chore: 构建/工具链相关
```

---

## 🚀 部署

### 使用 Docker Compose

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 生产环境部署

详细部署说明请查看 [DEPLOYMENT.md](./docs/DEPLOYMENT.md)

---

## 🧪 测试

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行测试并生成覆盖率报告
pytest --cov=src --cov-report=html

# 运行特定测试文件
pytest tests/test_characters.py
```

### 前端测试

```bash
cd frontend

# 运行所有测试
npm test

# 运行测试并生成覆盖率报告
npm test -- --coverage --watchAll=false

# 运行特定测试
npm test -- ErrorBoundary
```

### 测试覆盖率

| 模块 | 覆盖率 | 状态 |
|------|--------|------|
| 后端 API | - | ⚠️ 待完成 |
| 前端组件 | 85%+ | ✅ 完成 |
| 错误处理 | 96% | ✅ 完成 |
| 缓存系统 | - | ⚠️ 待完成 |

---

## 🤝 贡献

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

详细贡献指南请查看 [CONTRIBUTING.md](./docs/CONTRIBUTING.md)

### 贡献者

感谢所有贡献者的付出！

---

## 📊 项目状态

### 已完成功能 ✅

- [x] 基础架构搭建
- [x] 后端 API 错误处理系统
- [x] 前端错误边界和错误处理
- [x] Redis 缓存策略实现
- [x] 前端单元测试 (85%+ 覆盖率)
- [x] API 文档自动生成
- [x] 全局搜索功能

### 进行中 🔄

- [ ] 角色、武器、圣遗物数据爬虫
- [ ] 完善角色详情页面
- [ ] 后端单元测试

### 计划中 📅

- [ ] 生产环境部署
- [ ] 性能优化和监控
- [ ] 移动端 App

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 📧 联系方式

- **项目仓库**: https://github.com/lastdanger/genshin-wiki-infomation
- **问题反馈**: https://github.com/lastdanger/genshin-wiki-infomation/issues

---

<div align="center">

**如果这个项目对你有帮助，请给一个 ⭐ Star！**

Made with ❤️ by the Genshin Wiki Team

</div>
