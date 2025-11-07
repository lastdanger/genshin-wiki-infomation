# 🚀 GitHub 仓库设置快速指南

这是一个快速操作清单,帮助你完成 GitHub 仓库的完整设置。

---

## 📋 快速检查清单

### Phase 1: 基础信息设置 (5分钟)

- [ ] **1.1 仓库基本信息**
  - 仓库名称: `genshin-wiki-info`
  - 描述: `A comprehensive Genshin Impact information website providing character data, weapon stats, artifacts, monsters, and game mechanics - 原神游戏信息整合平台`
  - 网站: (部署后填写)
  - Topics: 添加以下标签
    ```
    genshin-impact, genshin, game-wiki, python, fastapi, react,
    postgresql, game-database, gaming, anime-games, mihoyo,
    hoyoverse, character-database, weapon-guide, game-guide
    ```

- [ ] **1.2 仓库设置 (Settings)**
  - ✅ Issues (启用)
  - ✅ Projects (启用)
  - ✅ Discussions (启用 - 推荐)
  - ❌ Wiki (可选)
  - ✅ Pull Requests (启用)

---

### Phase 2: Issue 模板配置 (已完成 ✅)

已创建的模板文件:
- ✅ `.github/ISSUE_TEMPLATE/config.yml` - Issue 配置
- ✅ `.github/ISSUE_TEMPLATE/bug_report.yml` - Bug 报告
- ✅ `.github/ISSUE_TEMPLATE/feature_request.yml` - 功能请求
- ✅ `.github/ISSUE_TEMPLATE/data_update.yml` - 数据更新
- ✅ `.github/ISSUE_TEMPLATE/documentation.yml` - 文档改进
- ✅ `.github/PULL_REQUEST_TEMPLATE.md` - PR 模板

**下一步:** 提交这些文件到 GitHub

---

### Phase 3: GitHub Projects 看板创建 (10分钟)

#### 3.1 创建项目

```bash
# Web 操作:
1. 访问你的 GitHub 仓库
2. 点击 "Projects" 标签
3. 点击 "New project"
4. 选择 "Board" 模板
5. 项目名称: "Genshin Wiki Info - Development"
6. 描述: "原神信息网站开发看板"
7. 点击 "Create"
```

#### 3.2 配置看板列

创建以下列 (从左到右):

| 序号 | 列名 | 英文名 | 说明 |
|------|------|--------|------|
| 1 | 📥 Backlog | Backlog | 待整理的需求 |
| 2 | 🎯 Ready | Ready | 准备开发 |
| 3 | 🔄 In Progress | In Progress | 开发中 |
| 4 | 👀 Review | Review | 代码审查 |
| 5 | 🧪 Testing | Testing | 测试中 |
| 6 | ✅ Done | Done | 已完成 |
| 7 | ❌ Blocked | Blocked | 被阻塞 |

#### 3.3 添加自定义字段

点击项目右上角 "⋯" → "Settings" → "Custom fields"

**字段 1: Priority (优先级)**
```
类型: Single Select
选项:
  🔥 P0 - Critical
  🔴 P1 - High
  🟡 P2 - Medium
  🟢 P3 - Low
```

**字段 2: Module (功能模块)**
```
类型: Single Select
选项:
  🎭 Character
  ⚔️ Weapon
  💎 Artifact
  👾 Monster
  📚 GameMechanic
  🖼️ Gallery
  🔧 Infrastructure
  🎨 Frontend
  ⚙️ Backend
  🗄️ Database
```

**字段 3: Type (任务类型)**
```
类型: Single Select
选项:
  ✨ Feature
  🐛 Bug
  📈 Enhancement
  🔄 Refactor
  📝 Documentation
  🧪 Test
  🚀 Performance
```

**字段 4: Estimate (工作量)**
```
类型: Number
说明: Story Points (1, 2, 3, 5, 8, 13)
```

**字段 5: Sprint (迭代)**
```
类型: Iteration
配置:
  Sprint 1: 2025-11-06 ~ 2025-11-19 (2周)
  Sprint 2: 2025-11-20 ~ 2025-12-03
  Sprint 3: 2025-12-04 ~ 2025-12-17
  Sprint 4: 2025-12-18 ~ 2025-12-31
```

#### 3.4 创建多视图

**视图 1: 状态视图 (默认)**
- 布局: Board
- 分组: Status
- 排序: Priority (高→低)

**视图 2: 优先级视图**
- 布局: Board
- 分组: Priority
- 排序: Module

**视图 3: 模块视图**
- 布局: Board
- 分组: Module
- 排序: Priority

**视图 4: Sprint 表格**
- 布局: Table
- 筛选: Sprint = Current Sprint
- 显示列: Title, Status, Priority, Module, Estimate, Assignee

**视图 5: 路线图**
- 布局: Roadmap
- 时间轴: 按 Sprint 分组

#### 3.5 配置自动化

点击项目右上角 "⋯" → "Workflows"

添加以下工作流:

```yaml
1. 新 Issue 进入 Backlog
   When: Item added to project
   Then: Set Status to "Backlog"

2. 分配任务后进入 In Progress
   When: Item assigned
   Then: Set Status to "In Progress"

3. PR 创建后进入 Review
   When: Pull request opened
   Then: Set Status to "Review"

4. PR 审批后进入 Testing
   When: Pull request approved
   Then: Set Status to "Testing"

5. PR 合并后进入 Done
   When: Pull request merged
   Then: Set Status to "Done"

6. Issue 关闭后进入 Done
   When: Item closed
   Then: Set Status to "Done"
```

---

### Phase 4: Labels 标签创建 (5分钟)

进入仓库 → Settings → Labels → New label

创建以下标签:

**优先级标签:**
| Name | Color | Description |
|------|-------|-------------|
| `priority: critical` | `#d73a4a` | P0 - 紧急关键 |
| `priority: high` | `#ff6b6b` | P1 - 高优先级 |
| `priority: medium` | `#ffd93d` | P2 - 中优先级 |
| `priority: low` | `#6bcf7f` | P3 - 低优先级 |

**类型标签:**
| Name | Color | Description |
|------|-------|-------------|
| `type: feature` | `#a2eeef` | 新功能 |
| `type: bug` | `#d73a4a` | Bug 修复 |
| `type: enhancement` | `#84b6eb` | 功能增强 |
| `type: documentation` | `#0075ca` | 文档相关 |
| `type: test` | `#1d76db` | 测试相关 |
| `type: refactor` | `#fbca04` | 代码重构 |
| `type: performance` | `#0e8a16` | 性能优化 |
| `type: data` | `#c5def5` | 数据相关 |

**模块标签:**
| Name | Color | Description |
|------|-------|-------------|
| `module: character` | `#e99695` | 角色模块 |
| `module: weapon` | `#f9d0c4` | 武器模块 |
| `module: artifact` | `#c5def5` | 圣遗物模块 |
| `module: monster` | `#bfdadc` | 怪物模块 |
| `module: frontend` | `#d4c5f9` | 前端 |
| `module: backend` | `#c2e0c6` | 后端 |
| `module: database` | `#fef2c0` | 数据库 |
| `module: infrastructure` | `#d1d5da` | 基础设施 |
| `module: data-crawler` | `#bfd4f2` | 数据爬虫 |

**状态标签:**
| Name | Color | Description |
|------|-------|-------------|
| `status: triage` | `#ffffff` | 待分类 |
| `status: blocked` | `#b60205` | 被阻塞 |
| `status: in-progress` | `#fbca04` | 进行中 |
| `status: needs-review` | `#0e8a16` | 需要审查 |

**其他标签:**
| Name | Color | Description |
|------|-------|-------------|
| `good first issue` | `#7057ff` | 适合新手 |
| `help wanted` | `#008672` | 需要帮助 |
| `question` | `#d876e3` | 问题咨询 |
| `duplicate` | `#cfd3d7` | 重复 Issue |
| `wontfix` | `#ffffff` | 不修复 |
| `invalid` | `#e4e669` | 无效 |

---

### Phase 5: 分支保护规则 (5分钟)

进入 Settings → Branches → Add branch protection rule

**保护 `main` 分支:**

```yaml
Branch name pattern: main

设置:
  ✅ Require a pull request before merging
    ✅ Require approvals: 1
    ✅ Dismiss stale pull request approvals when new commits are pushed
    ✅ Require review from Code Owners (可选)

  ✅ Require status checks to pass before merging
    ✅ Require branches to be up to date before merging
    选择需要的检查:
      - Backend CI
      - Frontend CI
      - Code Coverage

  ✅ Require conversation resolution before merging

  ✅ Include administrators (可选)

  ✅ Allow force pushes (仅特定人员)
  ❌ Allow deletions
```

**保护 `develop` 分支 (如果使用):**

```yaml
Branch name pattern: develop

设置:
  ✅ Require a pull request before merging
    ✅ Require approvals: 1
  ✅ Require status checks to pass before merging
```

---

### Phase 6: GitHub Actions 配置 (10分钟)

#### 6.1 创建 Backend CI

创建文件: `.github/workflows/backend-ci.yml`

```yaml
name: Backend CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'backend/**'
      - '.github/workflows/backend-ci.yml'
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
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: genshin_test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'

      - name: Install dependencies
        run: |
          cd backend
          pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Black
        run: |
          cd backend
          black --check app/ tests/

      - name: Run Flake8
        run: |
          cd backend
          flake8 app/ tests/ --max-line-length=88 --extend-ignore=E203

      - name: Run MyPy
        run: |
          cd backend
          mypy app/ --ignore-missing-imports

      - name: Run tests with coverage
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/genshin_test
          REDIS_URL: redis://localhost:6379/0
        run: |
          cd backend
          pytest tests/ -v --cov=app --cov-report=xml --cov-report=term-missing

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./backend/coverage.xml
          flags: backend
          name: backend-coverage
```

#### 6.2 创建 Frontend CI

创建文件: `.github/workflows/frontend-ci.yml`

```yaml
name: Frontend CI

on:
  push:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'
      - '.github/workflows/frontend-ci.yml'
  pull_request:
    branches: [ main, develop ]
    paths:
      - 'frontend/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Setup Node.js 18
        uses: actions/setup-node@v4
        with:
          node-version: '18'
          cache: 'npm'
          cache-dependency-path: frontend/package-lock.json

      - name: Install dependencies
        run: |
          cd frontend
          npm ci

      - name: Run ESLint
        run: |
          cd frontend
          npm run lint

      - name: Run Prettier check
        run: |
          cd frontend
          npm run format -- --check

      - name: Run tests with coverage
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false --maxWorkers=2

      - name: Build
        run: |
          cd frontend
          npm run build

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        with:
          file: ./frontend/coverage/coverage-final.json
          flags: frontend
          name: frontend-coverage
```

#### 6.3 自动添加 Issue 到 Project

创建文件: `.github/workflows/auto-add-to-project.yml`

```yaml
name: Auto Add to Project

on:
  issues:
    types: [opened]
  pull_request:
    types: [opened]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - name: Add to project
        uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/users/YOUR_USERNAME/projects/YOUR_PROJECT_NUMBER
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

**注意:** 需要将 `YOUR_USERNAME` 和 `YOUR_PROJECT_NUMBER` 替换为实际值。

---

### Phase 7: Security 安全设置 (3分钟)

进入 Settings → Security

- [ ] **Code security and analysis**
  - ✅ Dependabot alerts (启用)
  - ✅ Dependabot security updates (启用)
  - ✅ Dependabot version updates (启用)
  - ✅ Code scanning (可选)
  - ✅ Secret scanning (启用)

- [ ] **创建 Dependabot 配置**

创建文件: `.github/dependabot.yml`

```yaml
version: 2
updates:
  # Backend Python dependencies
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "type: dependencies"
      - "module: backend"

  # Frontend npm dependencies
  - package-ecosystem: "npm"
    directory: "/frontend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 5
    labels:
      - "type: dependencies"
      - "module: frontend"

  # GitHub Actions
  - package-ecosystem: "github-actions"
    directory: "/"
    schedule:
      interval: "monthly"
    labels:
      - "type: dependencies"
      - "module: infrastructure"
```

---

### Phase 8: 创建初始 Issues (10分钟)

参考 [PROJECT_BOARD_SETUP.md](PROJECT_BOARD_SETUP.md) 的 "初始任务列表" 部分。

快速创建前 5 个关键 Issue:

1. **[P0] Setup project structure and basic infrastructure**
2. **[P0] Setup CI/CD pipeline with GitHub Actions**
3. **[P1] Design database schema and setup Alembic migrations**
4. **[P1] Implement unified API service layer with error handling**
5. **[P1] Create frontend API service layer with Axios**

为每个 Issue 设置:
- Title (标题)
- Description (描述)
- Labels (标签)
- Module (模块)
- Priority (优先级)
- Estimate (估算)
- Add to Project (添加到看板)

---

### Phase 9: 文档完善 (可选)

- [ ] 创建 `CONTRIBUTING.md` (贡献指南)
- [ ] 创建 `CODE_OF_CONDUCT.md` (行为准则)
- [ ] 创建 `SECURITY.md` (安全政策)
- [ ] 更新 `README.md`
- [ ] 创建 `CHANGELOG.md`

---

## 🎯 验证清单

完成所有设置后,验证以下内容:

- [ ] 仓库信息和标签已设置
- [ ] Issue 模板正常工作 (创建一个测试 Issue)
- [ ] PR 模板正常工作
- [ ] GitHub Projects 看板已创建并配置
- [ ] 自定义字段和视图正常
- [ ] Labels 已创建
- [ ] 分支保护规则生效
- [ ] GitHub Actions workflows 正常运行
- [ ] Dependabot 配置正确
- [ ] 初始 Issues 已创建并添加到看板

---

## 📚 下一步

1. **开始第一个 Sprint**
   - 从 Backlog 选择任务到 Ready
   - 分配任务
   - 开始开发

2. **配置部署**
   - 设置 Production 环境
   - 配置 CD 流程
   - 准备域名和服务器

3. **邀请团队成员**
   - 添加 Collaborators
   - 分配角色和权限
   - 同步项目规划

---

## 🔗 相关文档

- [完整看板设置指南](PROJECT_BOARD_SETUP.md)
- [功能规格说明](specs/001-genshin-info-website/spec.md)
- [GitHub Projects 文档](https://docs.github.com/en/issues/planning-and-tracking-with-projects)

---

## 💡 提示

### 快速命令

```bash
# 批量创建标签 (使用 gh CLI)
gh label create "priority: critical" --color d73a4a --description "P0 - 紧急关键"
gh label create "priority: high" --color ff6b6b --description "P1 - 高优先级"
# ... 更多标签

# 创建 Issue
gh issue create --title "[P0] Setup project structure" --label "priority: critical,type: feature" --body "详细描述..."

# 查看当前 Sprint 的 Issue
gh issue list --label "sprint: 1"
```

### 时间估算

- Phase 1: 5 分钟
- Phase 2: 已完成
- Phase 3: 10 分钟
- Phase 4: 5 分钟
- Phase 5: 5 分钟
- Phase 6: 10 分钟
- Phase 7: 3 分钟
- Phase 8: 10 分钟
- Phase 9: 可选

**总计: 约 50 分钟**

---

最后更新: 2025-11-06
