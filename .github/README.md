# GitHub 自动化配置

本目录包含项目的所有 GitHub 自动化配置。

## 📁 目录结构

```
.github/
├── workflows/                      # GitHub Actions 工作流
│   ├── auto-add-to-project.yml    # 自动添加 Issue/PR 到项目看板
│   ├── backend-ci.yml             # 后端 CI/CD
│   ├── frontend-ci.yml            # 前端 CI/CD
│   ├── issue-labeler.yml          # Issue 自动标签
│   ├── pr-labeler.yml             # PR 自动标签
│   ├── project-automation.yml     # 项目看板状态自动化
│   └── dependency-update.yml      # 依赖安全检查
├── ISSUE_TEMPLATE/                # Issue 模板
│   ├── bug_report.yml
│   ├── feature_request.yml
│   ├── data_update.yml
│   ├── documentation.yml
│   └── config.yml
├── dependabot.yml                 # Dependabot 配置
├── labeler.yml                    # 基于文件路径的标签配置
├── pr-labeler.yml                 # 基于分支名称的标签配置
└── README.md                      # 本文件
```

## 🔄 工作流说明

### 1. Backend CI ([workflows/backend-ci.yml](workflows/backend-ci.yml))

**触发时机**: Push/PR 到 main/develop 分支 (backend 路径变化)

**功能:**
- 🔍 代码格式检查 (Black)
- 🔍 代码静态分析 (Flake8)
- 🔍 类型检查 (MyPy)
- 🧪 运行测试 + 覆盖率报告
- 🔐 安全漏洞扫描 (Trivy)
- 📊 上传覆盖率到 Codecov

**服务依赖:**
- PostgreSQL 14
- Redis 7

---

### 2. Frontend CI ([workflows/frontend-ci.yml](workflows/frontend-ci.yml))

**触发时机**: Push/PR 到 main/develop 分支 (frontend 路径变化)

**功能:**
- 🔍 ESLint 代码检查
- 🔍 Prettier 格式检查
- 🧪 运行测试 + 覆盖率报告
- 🏗️ 生产构建测试
- 📊 构建大小报告
- ⚡ Lighthouse 性能审计

**测试环境:**
- Node.js 18.x
- Node.js 20.x

---

### 3. PR Auto Labeler ([workflows/pr-labeler.yml](workflows/pr-labeler.yml))

**触发时机**: PR 打开/更新

**功能:**
- 🏷️ 基于修改文件自动添加标签 (使用 [labeler.yml](labeler.yml))
- 🏷️ 基于分支名称自动添加标签 (使用 [pr-labeler.yml](pr-labeler.yml))
- 🏷️ 基于 PR 标题和内容添加优先级标签
- 🏷️ 检测破坏性变更
- 🏷️ 标记 Draft PR
- 📏 自动添加代码变化量标签 (size/XS ~ XXL)

---

### 4. Issue Auto Labeler ([workflows/issue-labeler.yml](workflows/issue-labeler.yml))

**触发时机**: Issue 打开/编辑

**功能:**
- 🏷️ 基于标题和内容自动识别类型
- 🏷️ 自动识别优先级 ([P0], [P1], [P2], [P3])
- 🏷️ 自动识别模块 ([Character], [Weapon], etc.)
- 🏷️ 自动识别前后端标签
- 💬 新 Issue 自动发送欢迎消息

---

### 5. Project Automation ([workflows/project-automation.yml](workflows/project-automation.yml))

**触发时机**: Issue/PR 状态变化

**功能:**
- 📋 自动更新项目看板状态
- 🔄 Issue 状态映射:
  - opened → Backlog
  - assigned → In Progress
  - closed → Done
- 🔄 PR 状态映射:
  - opened (ready) → Review
  - approved → Testing
  - merged → Done
- 🔗 自动关闭 PR 中引用的 Issue
- 💬 状态变化时自动评论通知

---

### 6. Auto Add to Project ([workflows/auto-add-to-project.yml](workflows/auto-add-to-project.yml))

**触发时机**: Issue/PR 打开

**功能:**
- 📋 自动将新 Issue/PR 添加到项目看板

**需要配置:**
- `PROJECT_TOKEN` secret

---

### 7. Dependency Updates ([workflows/dependency-update.yml](workflows/dependency-update.yml))

**触发时机**: 每周一 09:00 UTC / 手动触发

**功能:**
- 🔐 检查后端依赖安全漏洞 (pip-audit)
- 🔐 检查前端依赖安全漏洞 (npm audit)
- 📋 发现漏洞时自动创建 Issue
- ✅ 自动批准 Dependabot 的 minor/patch 更新
- 🔄 自动合并小版本更新 (测试通过后)

---

## 🔐 Dependabot 配置 ([dependabot.yml](dependabot.yml))

**检查频率**: 每周一 09:00 (北京时间)

**监控的依赖:**
1. **Backend Python** (`/backend/requirements.txt`)
   - 最大 PR 数: 5
   - 标签: dependencies, ⚙️ backend

2. **Frontend NPM** (`/frontend/package.json`)
   - 最大 PR 数: 5
   - 标签: dependencies, 🎨 frontend
   - 分组: React 生态系统、开发依赖

3. **GitHub Actions** (`.github/workflows/*.yml`)
   - 最大 PR 数: 3
   - 标签: dependencies, 🔧 infrastructure

---

## 🏷️ 标签配置

### [labeler.yml](labeler.yml) - 基于文件路径

自动为修改特定路径的 PR 添加标签:

```yaml
'module: character':
  - backend/src/models/character*.py
  - frontend/src/pages/Characters/**/*

'🎨 frontend':
  - frontend/**/*

'⚙️ backend':
  - backend/**/*
```

### [pr-labeler.yml](pr-labeler.yml) - 基于分支名称

自动为特定分支名称的 PR 添加标签:

```yaml
feature/*: ['type: feature', '✨ feature']
fix/*: ['type: bug', '🐛 bug']
hotfix/*: ['type: bug', 'priority: critical']
```

---

## 🔑 必需的 Secrets

在仓库 Settings → Secrets → Actions 中配置:

### 1. PROJECT_TOKEN (必需)
- **用途**: 项目看板自动化
- **权限**: repo + project
- **创建**: https://github.com/settings/tokens

### 2. CODECOV_TOKEN (可选)
- **用途**: 代码覆盖率报告
- **创建**: https://codecov.io

---

## 📖 使用指南

详细的使用说明请查看:
- [GitHub Actions 自动化配置指南](../GITHUB_ACTIONS_GUIDE.md)
- [自动化配置总结](../AUTOMATION_SETUP_SUMMARY.md)
- [项目看板设置指南](../PROJECT_BOARD_SETUP.md)

---

## 🎯 快速开始

### 1. 配置 Secrets

```bash
# 1. 创建 GitHub Token
https://github.com/settings/tokens

# 2. 在仓库设置中添加 PROJECT_TOKEN
Settings → Secrets → Actions → New repository secret
```

### 2. 创建标签

运行以下命令或手动在 GitHub 中创建:

```bash
# 优先级标签
priority: critical, priority: high, priority: medium, priority: low

# 类型标签
type: feature, type: bug, type: enhancement, type: documentation

# 模块标签
module: character, module: weapon, module: artifact, module: monster

# 其他标签
🎨 frontend, ⚙️ backend, 🗄️ database, 🔧 infrastructure
good first issue, help wanted, blocked, dependencies
```

### 3. 测试自动化

```bash
# 创建测试 Issue
标题: [P1][Character] 测试自动标签

# 创建测试 PR
git checkout -b feature/test-automation
git commit --allow-empty -m "test: test automation"
git push origin feature/test-automation
```

---

## 🔧 故障排查

### Actions 失败

1. 查看 Actions 运行日志
2. 检查 Secrets 是否配置正确
3. 确认工作流文件语法正确

### 标签未自动添加

1. 检查 labeler.yml 配置
2. 查看 Actions 运行日志
3. 确认标签已在仓库中创建

### 项目看板未更新

1. 确认 PROJECT_TOKEN 已配置
2. 检查 token 权限 (需要 project 权限)
3. 查看 Actions 运行日志

---

## 📊 监控和维护

### 定期检查

- 📈 每周检查 CI/CD 运行时间
- 📊 每月审查代码覆盖率趋势
- 🔐 及时处理依赖漏洞 Issue
- 🔄 定期更新 Actions 版本

### 优化建议

- ⚡ 优化测试执行时间
- 📦 使用缓存加速构建
- 🎯 调整自动化规则
- 📝 更新文档

---

最后更新: 2025-11-07
