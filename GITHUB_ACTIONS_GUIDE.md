# GitHub Actions 自动化配置指南

本文档介绍项目中配置的所有 GitHub Actions 自动化工作流及其使用方法。

## 📋 目录

1. [工作流概览](#工作流概览)
2. [CI/CD 工作流](#cicd-工作流)
3. [自动化标签管理](#自动化标签管理)
4. [项目看板自动化](#项目看板自动化)
5. [依赖管理自动化](#依赖管理自动化)
6. [必需的 Secrets 配置](#必需的-secrets-配置)
7. [使用指南](#使用指南)
8. [故障排查](#故障排查)

---

## 🎯 工作流概览

### 已配置的工作流

| 工作流 | 文件 | 触发条件 | 主要功能 |
|--------|------|----------|----------|
| Backend CI | `backend-ci.yml` | Push/PR 到 backend | 后端代码检查、测试、安全扫描 |
| Frontend CI | `frontend-ci.yml` | Push/PR 到 frontend | 前端代码检查、测试、构建、性能审计 |
| PR Auto Labeler | `pr-labeler.yml` | PR 打开/更新 | 自动添加标签到 PR |
| Issue Auto Labeler | `issue-labeler.yml` | Issue 打开/编辑 | 自动添加标签到 Issue |
| Project Automation | `project-automation.yml` | Issue/PR 状态变化 | 自动更新项目看板状态 |
| Auto Add to Project | `auto-add-to-project.yml` | Issue/PR 打开 | 自动添加到项目看板 |
| Dependency Updates | `dependency-update.yml` | 每周一/手动 | 检查依赖安全漏洞 |
| Dependabot | `dependabot.yml` | 每周一 | 自动创建依赖更新 PR |

---

## 🔄 CI/CD 工作流

### 1. Backend CI

**触发条件:**
- Push 到 `main` 或 `develop` 分支(backend 路径变化时)
- PR 到 `main` 或 `develop` 分支(backend 路径变化时)

**执行步骤:**

#### Lint and Test Job
1. 设置 PostgreSQL 和 Redis 服务
2. 安装 Python 3.11 和依赖
3. 运行代码格式检查(Black)
4. 运行代码静态检查(Flake8)
5. 运行类型检查(MyPy)
6. 运行测试并生成覆盖率报告
7. 上传覆盖率到 Codecov
8. 在 PR 中评论覆盖率变化

#### Security Scan Job
1. 使用 Trivy 扫描代码漏洞
2. 上传结果到 GitHub Security

**质量门槛:**
- 代码覆盖率最低: 70% (绿色), 50% (橙色)
- Black 格式检查必须通过
- Flake8 严重错误必须修复

---

### 2. Frontend CI

**触发条件:**
- Push 到 `main` 或 `develop` 分支(frontend 路径变化时)
- PR 到 `main` 或 `develop` 分支(frontend 路径变化时)

**执行步骤:**

#### Lint and Test Job
运行在 Node.js 18.x 和 20.x 上:
1. 安装依赖(`npm ci`)
2. 运行 ESLint 检查
3. 运行 Prettier 格式检查
4. 运行测试并生成覆盖率
5. 上传覆盖率到 Codecov
6. 构建生产版本
7. 检查并报告构建大小
8. 上传构建产物(保留 7 天)

#### Lighthouse Audit Job
1. 构建应用
2. 运行 Lighthouse 性能审计(3 次)
3. 上传审计报告

---

## 🏷️ 自动化标签管理

### 3. PR Auto Labeler

**自动添加的标签:**

#### 基于文件路径
- 修改 `backend/**` → 添加 `⚙️ backend`
- 修改 `frontend/**` → 添加 `🎨 frontend`
- 修改角色相关文件 → 添加 `module: character`
- 修改测试文件 → 添加 `🧪 test`

#### 基于分支名称
- `feature/*` → 添加 `type: feature`, `✨ feature`
- `fix/*` → 添加 `type: bug`, `🐛 bug`
- `hotfix/*` → 添加 `type: bug`, `priority: critical`

#### 基于 PR 内容
- 标题包含 `[P0]` → 添加 `priority: critical`
- 标题包含 `breaking` → 添加 `⚠️ breaking change`
- PR 是 Draft → 添加 `🚧 work in progress`

#### 基于代码变化量
- 0-10 行 → `size/XS`
- 10-50 行 → `size/S`
- 50-200 行 → `size/M`
- 200-500 行 → `size/L`
- 500-1000 行 → `size/XL`
- 1000+ 行 → `size/XXL`

---

### 4. Issue Auto Labeler

**自动添加的标签:**

| 标题/内容关键词 | 添加的标签 |
|----------------|-----------|
| [P0], critical | priority: critical |
| [P1], urgent | priority: high |
| bug, fix | type: bug, 🐛 bug |
| feature, feat | type: feature, ✨ feature |
| [character] | module: character, 🎭 character |
| [backend] | ⚙️ backend |
| security | 🔐 security |

**自动欢迎消息:**
新 Issue 会收到自动回复,引导用户提供更多信息。

---

## 📊 项目看板自动化

### 5. Project Automation

**自动化规则:**

#### Issue 状态映射
| Issue 事件 | 项目看板状态 |
|-----------|-------------|
| opened | Backlog |
| assigned | In Progress |
| closed | Done |
| reopened | Ready |

#### PR 状态映射
| PR 事件 | 项目看板状态 |
|---------|-------------|
| opened (draft) | In Progress |
| opened (ready) | Review |
| ready_for_review | Review |
| converted_to_draft | In Progress |
| closed + merged | Done |
| closed + not merged | Backlog |

#### PR 审核状态映射
| 审核状态 | 项目看板状态 |
|---------|-------------|
| approved | Testing |
| changes_requested | In Progress |

#### 关联 Issue 自动关闭
当 PR 合并时,自动关闭 PR 中引用的 Issue:
- 支持关键词: `close`, `closes`, `closed`, `fix`, `fixes`, `fixed`, `resolve`, `resolves`, `resolved`
- 示例: PR body 包含 "Fixes #123" → Issue #123 自动关闭

---

## 🔐 依赖管理自动化

### 7. Dependency Updates

**触发条件:**
- 每周一上午 9:00 UTC (北京时间 17:00)
- 手动触发

**功能:**

#### Backend 依赖检查
1. 使用 `pip-audit` 扫描 requirements.txt
2. 检测安全漏洞
3. 上传审计结果
4. 如果发现漏洞,自动创建 Issue

#### Frontend 依赖检查
1. 运行 `npm audit`
2. 检查过期的包
3. 上传审计结果
4. 如果发现漏洞,自动创建 Issue

#### Dependabot PR 自动合并
- 自动批准 minor 和 patch 版本更新
- 自动合并小版本更新(需要测试通过)

---

### 8. Dependabot

**配置:**

#### Backend Python 依赖
- 包管理器: pip
- 目录: `/backend`
- 检查频率: 每周一 09:00 (北京时间)
- 最大 PR 数: 5

#### Frontend NPM 依赖
- 包管理器: npm
- 目录: `/frontend`
- 检查频率: 每周一 09:00 (北京时间)
- 最大 PR 数: 5
- 分组更新: React 生态系统、开发依赖

#### GitHub Actions 依赖
- 包管理器: github-actions
- 目录: `/`
- 检查频率: 每周一 09:00 (北京时间)
- 最大 PR 数: 3

---

## 🔑 必需的 Secrets 配置

在 GitHub 仓库设置中配置以下 Secrets:

### 1. PROJECT_TOKEN (必需)

用于项目看板自动化和自动添加 Issue/PR 到项目。

**创建步骤:**
1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 选择权限:
   - `repo` (Full control of private repositories)
   - `project` (Full control of projects)
4. 生成 token 并复制
5. 在仓库 Settings → Secrets → Actions → New repository secret
6. 名称: `PROJECT_TOKEN`
7. 值: 粘贴 token

### 2. CODECOV_TOKEN (可选)

用于上传代码覆盖率报告。

**创建步骤:**
1. 访问 https://codecov.io
2. 使用 GitHub 账号登录
3. 添加仓库
4. 复制 token
5. 在仓库 Settings → Secrets → Actions → New repository secret
6. 名称: `CODECOV_TOKEN`
7. 值: 粘贴 token

---

## 📖 使用指南

### 创建 Issue

**推荐命名格式:**
```
[模块] 简短描述

示例:
[Character] 角色详情页显示异常
[P1][Backend] API 响应时间过长
[Frontend] 添加角色筛选功能
```

---

### 创建 Pull Request

**推荐分支命名:**
```
类型/简短描述

示例:
feature/character-list
fix/api-timeout
hotfix/security-vulnerability
```

**推荐 PR 标题:**
```
[模块] 简短描述

示例:
[Character] 实现角色列表页面
[P0][Backend] 修复 SQL 注入漏洞
[Frontend] 优化角色卡片性能
```

**PR 描述模板:**
```markdown
## 🎯 目的
<!-- 这个 PR 解决什么问题或添加什么功能 -->

## 📝 变更内容
- [ ] 添加了 XXX 功能
- [ ] 修复了 XXX Bug
- [ ] 重构了 XXX 代码

## 🔗 关联 Issue
Closes #123

## 🧪 测试
- [ ] 单元测试通过
- [ ] 手动测试通过
- [ ] 集成测试通过

## 📸 截图
<!-- 如有 UI 变更,请提供截图 -->
```

---

### 代码提交规范

**推荐 Commit Message 格式:**
```
<type>(<scope>): <subject>

示例:
feat(character): add character list page
fix(api): fix timeout issue in character service
refactor(frontend): simplify character card component
test(backend): add tests for character API
docs(readme): update setup instructions
chore(deps): update dependencies
```

**Type 类型:**
- `feat`: 新功能
- `fix`: Bug 修复
- `refactor`: 代码重构
- `test`: 测试相关
- `docs`: 文档更新
- `chore`: 构建/工具相关
- `perf`: 性能优化
- `style`: 代码格式

---

## 🔧 故障排查

### CI 失败常见问题

#### Backend CI 失败

**Black 格式检查失败**
```bash
cd backend
black src/
git add .
git commit -m "style: format code with black"
```

**Flake8 检查失败**
```bash
cd backend
flake8 src/
# 根据提示修复代码
```

**测试失败**
```bash
cd backend
pytest tests/ -v
```

#### Frontend CI 失败

**ESLint 检查失败**
```bash
cd frontend
npm run lint:fix
git add .
git commit -m "style: fix eslint errors"
```

**构建失败**
```bash
cd frontend
npm run build
# 查看构建错误并修复
```

---

## 📈 最佳实践

### 开发流程

```
1. 创建 Issue 描述需求或 Bug
   ↓ (自动添加到项目看板 Backlog)

2. 从 Issue 创建分支 (feature/xxx 或 fix/xxx)
   ↓

3. 开发并提交代码 (遵循 Commit Message 规范)
   ↓

4. 推送到远程并创建 PR
   ↓ (自动运行 CI/CD)
   ↓ (自动添加标签)
   ↓ (自动移动到 Review 列)

5. Code Review
   ↓ (审核通过自动移动到 Testing 列)

6. 合并 PR
   ↓ (自动移动到 Done 列)
   ↓ (自动关闭关联的 Issue)

7. 完成!
```

### 标签使用建议

每个 Issue/PR 至少应该有:
- 1 个类型标签 (type: xxx)
- 1 个优先级标签 (priority: xxx)
- 1 个模块标签 (module: xxx)

### 代码质量要求

**Backend:**
- 代码覆盖率 ≥ 70%
- Black 格式化通过
- Flake8 检查通过

**Frontend:**
- 代码覆盖率 ≥ 60%
- ESLint 检查通过
- Prettier 格式化通过
- Lighthouse 性能分数 ≥ 90

---

## 🔗 相关资源

- [GitHub Actions 官方文档](https://docs.github.com/en/actions)
- [项目看板设置指南](PROJECT_BOARD_SETUP.md)
- [手动项目设置指南](MANUAL_PROJECT_SETUP.md)

---

最后更新: 2025-11-07
