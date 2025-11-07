# GitHub Projects 看板设置指南

## 📋 目录

1. [看板结构](#看板结构)
2. [实施步骤](#实施步骤)
3. [初始任务列表](#初始任务列表)
4. [自动化配置](#自动化配置)
5. [最佳实践](#最佳实践)

---

## 🎯 看板结构

### 推荐方案: 混合看板 (Hybrid Board)

**主视图 - 状态视图 (默认)**

| 列名 | 说明 | 颜色 |
|------|------|------|
| 📥 Backlog | 待整理的需求和想法 | 灰色 |
| 🎯 Ready | 已整理,准备开发 | 蓝色 |
| 🔄 In Progress | 正在开发中 | 黄色 |
| 👀 Review | 代码审查中 | 橙色 |
| 🧪 Testing | 测试中 | 紫色 |
| ✅ Done | 已完成 | 绿色 |
| ❌ Blocked | 被阻塞 | 红色 |

---

## 🛠️ 实施步骤

### Step 1: 创建 GitHub Project

```bash
# Web 操作步骤:
1. 访问: https://github.com/YOUR_USERNAME/genshin-wiki-info
2. 点击 "Projects" 标签
3. 点击 "New project"
4. 选择 "Board" 模板
5. 项目名称: "Genshin Wiki Info - Development"
6. 描述: "原神信息网站开发看板"
```

### Step 2: 配置自定义字段

#### 2.1 Priority (优先级)
```
类型: Single Select
选项:
  - 🔥 P0 - Critical
  - 🔴 P1 - High
  - 🟡 P2 - Medium
  - 🟢 P3 - Low
```

#### 2.2 Module (功能模块)
```
类型: Single Select
选项:
  - 🎭 Character
  - ⚔️ Weapon
  - 💎 Artifact
  - 👾 Monster
  - 📚 GameMechanic
  - 🖼️ Gallery
  - 🔧 Infrastructure
  - 🎨 Frontend
  - ⚙️ Backend
  - 🗄️ Database
```

#### 2.3 Type (任务类型)
```
类型: Single Select
选项:
  - ✨ Feature
  - 🐛 Bug
  - 📈 Enhancement
  - 🔄 Refactor
  - 📝 Documentation
  - 🧪 Test
  - 🚀 Performance
```

#### 2.4 Estimate (工作量)
```
类型: Number
单位: Story Points
常用值: 1, 2, 3, 5, 8, 13
```

#### 2.5 Sprint (迭代)
```
类型: Iteration
配置:
  - Sprint 1: 2025-11-06 ~ 2025-11-19
  - Sprint 2: 2025-11-20 ~ 2025-12-03
  - Sprint 3: 2025-12-04 ~ 2025-12-17
  - Sprint 4: 2025-12-18 ~ 2025-12-31
```

### Step 3: 配置视图 (Views)

#### 视图 1: 状态视图 (Status Board)
- 布局: Board
- 分组依据: Status
- 排序: Priority (高到低)

#### 视图 2: 优先级视图 (Priority Board)
- 布局: Board
- 分组依据: Priority
- 排序: Module

#### 视图 3: 模块视图 (Module Board)
- 布局: Board
- 分组依据: Module
- 排序: Priority

#### 视图 4: Sprint 视图 (Sprint Table)
- 布局: Table
- 筛选: Sprint = "Current Sprint"
- 排序: Priority
- 显示列: Title, Status, Priority, Estimate, Assignee

#### 视图 5: 甘特图视图 (Roadmap)
- 布局: Roadmap
- 时间轴: 显示 Due Date
- 分组依据: Module

### Step 4: 设置自动化规则

在项目设置中添加以下 Workflows:

```yaml
# Workflow 1: 新 Issue 自动进入 Backlog
When: Item added to project
Then: Set Status to "Backlog"

# Workflow 2: Issue 被分配时移至 In Progress
When: Item is assigned
Then: Set Status to "In Progress"

# Workflow 3: PR 创建时移至 Review
When: Pull request opened
Then: Set Status to "Review"

# Workflow 4: PR 审批后移至 Testing
When: Pull request approved
Then: Set Status to "Testing"

# Workflow 5: PR 合并后移至 Done
When: Pull request merged
Then: Set Status to "Done"

# Workflow 6: Issue 关闭时移至 Done
When: Item closed
Then: Set Status to "Done"
```

---

## 📝 初始任务列表

### Phase 0: 基础设施搭建 (Sprint 1)

#### 🔧 Infrastructure

**[P0] 项目初始化**
```
标题: Setup project structure and basic infrastructure
模块: Infrastructure
类型: Feature
优先级: P0
估算: 5 points
描述:
- [ ] 创建 backend 和 frontend 基础结构
- [ ] 配置 Docker Compose
- [ ] 设置 PostgreSQL 和 Redis
- [ ] 配置环境变量模板
```

**[P0] CI/CD 流水线**
```
标题: Setup CI/CD pipeline with GitHub Actions
模块: Infrastructure
类型: Feature
优先级: P0
估算: 8 points
描述:
- [ ] 配置 backend 测试和代码检查
- [ ] 配置 frontend 测试和构建
- [ ] 设置自动化部署
- [ ] 配置 Docker 镜像构建
```

**[P1] 数据库设计和迁移**
```
标题: Design database schema and setup Alembic migrations
模块: Database
类型: Feature
优先级: P1
估算: 8 points
描述:
- [ ] 设计角色、武器、圣遗物等表结构
- [ ] 创建 SQLAlchemy 模型
- [ ] 编写 Alembic 迁移脚本
- [ ] 添加测试数据种子
```

**[P1] API Service 基础层**
```
标题: Implement unified API service layer with error handling
模块: Backend
类型: Feature
优先级: P1
估算: 5 points
描述:
- [ ] 创建 API Service 基类
- [ ] 实现请求/响应拦截器
- [ ] 统一错误处理机制
- [ ] 添加日志记录
```

**[P1] 前端统一 API 封装**
```
标题: Create frontend API service layer with Axios
模块: Frontend
类型: Feature
优先级: P1
估算: 5 points
描述:
- [ ] 创建 axios 实例配置
- [ ] 实现请求/响应拦截器
- [ ] 统一错误处理
- [ ] 创建 API service 模块
参考: specs/001-genshin-info-website/spec.md - FR-011
```

---

### Phase 1: 核心功能开发 (Sprint 2-3)

#### 🎭 Character Module (P1)

**[P1] 角色列表页面**
```
标题: Implement character list page with filters
模块: Character
类型: Feature
优先级: P1
估算: 8 points
描述:
- [ ] 后端: 角色列表 API
- [ ] 前端: 角色卡片组件
- [ ] 筛选功能: 元素、武器类型、星级
- [ ] 搜索功能
- [ ] 分页加载
```

**[P1] 角色详情页面**
```
标题: Implement character detail page with full information
模块: Character
类型: Feature
优先级: P1
估算: 13 points
描述:
- [ ] 后端: 角色详情 API
- [ ] 前端: 基本信息展示
- [ ] 技能信息展示
- [ ] 天赋关系图可视化
- [ ] 推荐配装
```

**[P2] 角色数据爬虫**
```
标题: Implement web scraper for character data
模块: Character + Backend
类型: Feature
优先级: P2
估算: 13 points
描述:
- [ ] 从米游社 Wiki 爬取角色数据
- [ ] 从玉衡杯数据库同步数据
- [ ] 数据清洗和标准化
- [ ] 自动更新任务调度
```

#### ⚔️ Weapon Module (P2)

**[P2] 武器列表和详情**
```
标题: Implement weapon list and detail pages
模块: Weapon
类型: Feature
优先级: P2
估算: 8 points
描述:
- [ ] 后端: 武器 CRUD API
- [ ] 前端: 武器列表页面
- [ ] 前端: 武器详情页面
- [ ] 武器对比功能
```

**[P2] 武器数据爬虫**
```
标题: Implement web scraper for weapon data
模块: Weapon + Backend
类型: Feature
优先级: P2
估算: 8 points
描述:
- [ ] 爬取武器基础数据
- [ ] 爬取武器特效说明
- [ ] 推荐角色配对数据
```

#### 💎 Artifact Module (P2)

**[P2] 圣遗物列表和详情**
```
标题: Implement artifact set list and detail pages
模块: Artifact
类型: Feature
优先级: P2
估算: 8 points
描述:
- [ ] 后端: 圣遗物 API
- [ ] 前端: 套装列表页面
- [ ] 前端: 套装详情页面
- [ ] 词条推荐展示
```

#### 👾 Monster Module (P3)

**[P3] 怪物图鉴**
```
标题: Implement monster encyclopedia
模块: Monster
类型: Feature
优先级: P3
估算: 8 points
描述:
- [ ] 后端: 怪物数据 API
- [ ] 前端: 怪物列表页面
- [ ] 前端: 怪物详情页面
- [ ] 技能机制说明
```

#### 📚 Game Mechanics Module (P3)

**[P3] 游戏机制说明**
```
标题: Implement game mechanics documentation
模块: GameMechanic
类型: Feature
优先级: P3
估算: 5 points
描述:
- [ ] 基础机制页面
- [ ] 进阶攻略页面
- [ ] 元素反应计算器
```

#### 🖼️ Gallery Module (P3)

**[P3] 角色图片管理**
```
标题: Implement character gallery with upload
模块: Gallery
类型: Feature
优先级: P3
估算: 13 points
描述:
- [ ] 后端: 图片上传 API
- [ ] 前端: 图片展示组件
- [ ] 图片审核机制
- [ ] OSS 存储集成
```

---

### Phase 2: 优化和完善 (Sprint 4)

#### 🚀 Performance (P2)

**[P2] 性能优化**
```
标题: Optimize application performance
模块: Frontend + Backend
类型: Performance
优先级: P2
估算: 8 points
描述:
- [ ] 实现 Redis 缓存
- [ ] 前端代码分割
- [ ] 图片懒加载
- [ ] API 响应时间优化
```

**[P2] SEO 优化**
```
标题: Implement SEO optimization
模块: Frontend
类型: Enhancement
优先级: P2
估算: 5 points
描述:
- [ ] 添加 meta tags
- [ ] 实现服务端渲染 (可选)
- [ ] 生成 sitemap
- [ ] 优化页面标题和描述
```

#### 🧪 Testing (P1)

**[P1] 后端测试覆盖**
```
标题: Add comprehensive backend tests
模块: Backend
类型: Test
优先级: P1
估算: 8 points
描述:
- [ ] API 端点测试
- [ ] 数据库模型测试
- [ ] 爬虫功能测试
- [ ] 达到 80% 代码覆盖率
```

**[P1] 前端测试覆盖**
```
标题: Add comprehensive frontend tests
模块: Frontend
类型: Test
优先级: P1
估算: 8 points
描述:
- [ ] 组件单元测试
- [ ] API service 测试
- [ ] E2E 测试关键流程
- [ ] 达到 70% 代码覆盖率
```

#### 📝 Documentation (P2)

**[P2] 完善文档**
```
标题: Complete project documentation
模块: Documentation
类型: Documentation
优先级: P2
估算: 5 points
描述:
- [ ] 完善 README
- [ ] API 文档
- [ ] 部署文档
- [ ] 贡献指南
```

---

## 🤖 自动化配置

### GitHub Actions Workflows

创建 `.github/workflows/` 目录并添加以下文件:

#### 1. backend-ci.yml
```yaml
name: Backend CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'backend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:14
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
      - name: Run linters
        run: |
          cd backend
          black --check .
          flake8 .
          mypy .
      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v3
```

#### 2. frontend-ci.yml
```yaml
name: Frontend CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json
      - name: Install dependencies
        run: |
          cd frontend
          npm ci
      - name: Run linters
        run: |
          cd frontend
          npm run lint
      - name: Run tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false
      - name: Build
        run: |
          cd frontend
          npm run build
```

#### 3. auto-assign-project.yml
```yaml
name: Auto Assign to Project

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/users/YOUR_USERNAME/projects/PROJECT_NUMBER
          github-token: ${{ secrets.ADD_TO_PROJECT_PAT }}
```

---

## 🎯 最佳实践

### 1. Issue 命名规范

```
格式: [模块] 简短描述 (不超过 60 字符)

示例:
✅ [Character] Implement character list API
✅ [Frontend] Add error boundary component
✅ [Bug] Fix weapon detail page crash
❌ fix bug (太模糊)
❌ 实现角色系统的所有功能包括列表详情和搜索 (太长)
```

### 2. Label 使用规范

建议创建以下 Labels:

| Label | 颜色 | 用途 |
|-------|------|------|
| `priority: critical` | #d73a4a | P0 任务 |
| `priority: high` | #ff6b6b | P1 任务 |
| `priority: medium` | #ffd93d | P2 任务 |
| `priority: low` | #6bcf7f | P3 任务 |
| `type: feature` | #a2eeef | 新功能 |
| `type: bug` | #d73a4a | Bug 修复 |
| `type: enhancement` | #84b6eb | 功能增强 |
| `type: documentation` | #0075ca | 文档相关 |
| `module: character` | #e99695 | 角色模块 |
| `module: weapon` | #f9d0c4 | 武器模块 |
| `module: artifact` | #c5def5 | 圣遗物模块 |
| `good first issue` | #7057ff | 适合新手 |
| `help wanted` | #008672 | 需要帮助 |
| `blocked` | #ffffff | 被阻塞 |

### 3. Sprint 规划流程

```
Sprint 周期: 2周

Week 1 - Day 1 (周一):
  - Sprint Planning 会议
  - 从 Backlog 选择任务到 Ready
  - 分配任务给团队成员

Week 1 - Day 2-5:
  - 开发阶段
  - Daily Standup (每日同步)
  - 移动任务状态

Week 2 - Day 1-4:
  - 继续开发
  - Code Review
  - Testing

Week 2 - Day 5 (周五):
  - Sprint Review (演示完成功能)
  - Sprint Retrospective (回顾改进)
  - 准备下一个 Sprint
```

### 4. 任务估算指南

**Story Points 参考:**

| Points | 复杂度 | 时间 | 示例 |
|--------|--------|------|------|
| 1 | 非常简单 | 1-2h | 修改配置、简单文档 |
| 2 | 简单 | 2-4h | 小功能、简单组件 |
| 3 | 中等 | 4-8h | 标准 CRUD、普通页面 |
| 5 | 复杂 | 1-2天 | 复杂页面、API 设计 |
| 8 | 很复杂 | 2-3天 | 核心模块、数据爬虫 |
| 13 | 非常复杂 | 3-5天 | 大型功能、架构改动 |

**如果任务超过 13 points，应该拆分成更小的子任务。**

### 5. Code Review 检查清单

```markdown
## Code Review Checklist

- [ ] 代码符合项目编码规范
- [ ] 所有测试通过
- [ ] 添加了必要的测试用例
- [ ] 代码无明显的 bug 和安全漏洞
- [ ] API 文档已更新 (如有变更)
- [ ] 性能没有明显下降
- [ ] 没有遗留的 console.log 或调试代码
- [ ] Commit message 清晰明确
- [ ] 符合原始 Issue 的需求
```

### 6. 每日站会模板

```markdown
## Daily Standup - YYYY-MM-DD

### @your-name
- 昨天完成:
  - [x] 完成角色列表 API
  - [x] Code review #123

- 今天计划:
  - [ ] 实现角色详情 API
  - [ ] 编写单元测试

- 遇到的问题:
  - 数据库查询性能需要优化

### @teammate
...
```

---

## 📊 看板使用流程图

```
┌─────────────────┐
│  新需求或 Bug   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  📥 Backlog     │ ← Issue 自动进入
│  (待整理)       │
└────────┬────────┘
         │ 整理和评估
         ▼
┌─────────────────┐
│  🎯 Ready       │ ← Sprint Planning 选择
│  (准备开发)     │
└────────┬────────┘
         │ 分配任务
         ▼
┌─────────────────┐
│  🔄 In Progress │ ← 开发中
│  (开发中)       │
└────────┬────────┘
         │ 提交 PR
         ▼
┌─────────────────┐
│  👀 Review      │ ← Code Review
│  (代码审查)     │
└────────┬────────┘
         │ 审批通过
         ▼
┌─────────────────┐
│  🧪 Testing     │ ← QA 测试
│  (测试中)       │
└────────┬────────┘
         │ 测试通过
         ▼
┌─────────────────┐
│  ✅ Done        │ ← PR 合并
│  (已完成)       │
└─────────────────┘

      任何阶段
         │
         ▼ 遇到阻塞
┌─────────────────┐
│  ❌ Blocked     │
│  (被阻塞)       │
└─────────────────┘
```

---

## 🔗 相关资源

- [GitHub Projects 官方文档](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [敏捷开发最佳实践](https://www.atlassian.com/agile)
- [Scrum 指南](https://scrumguides.org/)
- [项目管理工具对比](https://github.com/ripienaar/free-for-dev#project-management)

---

## 📞 支持

如有问题,请在项目中创建 Issue 或联系项目维护者。

最后更新: 2025-11-06
