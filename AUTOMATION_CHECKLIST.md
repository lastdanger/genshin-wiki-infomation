# 🚀 GitHub Actions 自动化配置检查清单

使用本清单确保所有自动化功能正确配置。

## ✅ 配置检查清单

### 📁 文件配置

- [x] `.github/workflows/backend-ci.yml` - 后端 CI/CD
- [x] `.github/workflows/frontend-ci.yml` - 前端 CI/CD  
- [x] `.github/workflows/pr-labeler.yml` - PR 自动标签
- [x] `.github/workflows/issue-labeler.yml` - Issue 自动标签
- [x] `.github/workflows/project-automation.yml` - 项目看板自动化
- [x] `.github/workflows/auto-add-to-project.yml` - 自动添加到项目
- [x] `.github/workflows/dependency-update.yml` - 依赖更新检查
- [x] `.github/dependabot.yml` - Dependabot 配置
- [x] `.github/labeler.yml` - 文件路径标签配置
- [x] `.github/pr-labeler.yml` - 分支名称标签配置

### 🔑 GitHub Secrets (需要手动配置)

- [ ] `PROJECT_TOKEN` - 项目看板自动化 **(必需)**
  - 权限: repo + project
  - 创建地址: https://github.com/settings/tokens
  
- [ ] `CODECOV_TOKEN` - 代码覆盖率报告 **(可选)**
  - 创建地址: https://codecov.io

### 🏷️ GitHub Labels (需要手动创建)

#### 优先级标签
- [ ] `priority: critical` (#d73a4a)
- [ ] `priority: high` (#ff6b6b)
- [ ] `priority: medium` (#ffd93d)
- [ ] `priority: low` (#6bcf7f)

#### 类型标签
- [ ] `type: feature` (#a2eeef) ✨ feature
- [ ] `type: bug` (#d73a4a) 🐛 bug
- [ ] `type: enhancement` (#84b6eb) 📈 enhancement
- [ ] `type: documentation` (#0075ca) 📝 documentation
- [ ] `type: test` (#c5def5) 🧪 test
- [ ] `type: refactor` (#fbca04) 🔄 refactor
- [ ] `type: performance` (#ff9800) 🚀 performance
- [ ] `type: chore` (#fef2c0)

#### 模块标签
- [ ] `module: character` (#e99695) 🎭
- [ ] `module: weapon` (#f9d0c4) ⚔️
- [ ] `module: artifact` (#c5def5) 💎
- [ ] `module: monster` (#bfdadc) 👾
- [ ] `module: game mechanics` (#d4c5f9) 📚
- [ ] `module: gallery` (#c2e0c6) 🖼️

#### 前后端标签
- [ ] `🎨 frontend` (#0052cc)
- [ ] `⚙️ backend` (#5319e7)
- [ ] `��️ database` (#1d76db)
- [ ] `🔧 infrastructure` (#ededed)

#### 特殊标签
- [ ] `good first issue` (#7057ff)
- [ ] `help wanted` (#008672)
- [ ] `blocked` (#b60205)
- [ ] `🚧 work in progress` (#fbca04)
- [ ] `⚠️ breaking change` (#d73a4a)
- [ ] `🔐 security` (#ee0701)
- [ ] `dependencies` (#0366d6)

#### 大小标签
- [ ] `size/XS` (#00ff00)
- [ ] `size/S` (#7fff00)
- [ ] `size/M` (#ffff00)
- [ ] `size/L` (#ff7f00)
- [ ] `size/XL` (#ff0000)
- [ ] `size/XXL` (#8b0000)

### ⚙️ Dependabot 设置

- [ ] 启用 Dependabot alerts
  - Settings → Security → Code security → Dependabot alerts
  
- [ ] 启用 Dependabot security updates
  - Settings → Security → Code security → Dependabot security updates

### 🧪 测试验证

#### Issue 自动化测试
- [ ] 创建测试 Issue: `[P1][Character] 测试自动标签`
- [ ] 验证标签自动添加
- [ ] 验证自动添加到项目看板
- [ ] 验证自动欢迎消息

#### PR 自动化测试
- [ ] 创建测试分支: `feature/test-automation`
- [ ] 创建测试 PR
- [ ] 验证标签自动添加 (类型、模块、大小)
- [ ] 验证 CI/CD 自动运行
- [ ] 验证自动添加到项目看板

#### CI/CD 测试
- [ ] Backend CI 正常运行
- [ ] Frontend CI 正常运行
- [ ] 代码覆盖率报告生成
- [ ] 安全扫描正常运行

#### 项目看板测试
- [ ] Issue 分配时自动移至 In Progress
- [ ] PR 创建时自动移至 Review
- [ ] PR 审核通过时自动移至 Testing
- [ ] PR 合并时自动移至 Done
- [ ] 关联 Issue 自动关闭

### 📝 文档

- [x] AUTOMATION_SETUP_SUMMARY.md - 配置总结
- [x] GITHUB_ACTIONS_GUIDE.md - 详细使用指南
- [x] .github/README.md - GitHub 配置说明
- [x] AUTOMATION_CHECKLIST.md - 本检查清单

---

## 🎯 快速配置命令

### 1. 创建 PROJECT_TOKEN

```bash
# 1. 访问 GitHub Token 设置页面
open https://github.com/settings/tokens

# 2. 点击 "Generate new token (classic)"
# 3. 选择权限: repo + project
# 4. 生成并复制 token
# 5. 在仓库设置中添加 Secret
open https://github.com/YOUR_USERNAME/YOUR_REPO/settings/secrets/actions
```

### 2. 批量创建标签 (可选)

创建 `create-labels.sh` 脚本:

```bash
#!/bin/bash

# GitHub repo info
OWNER="your-username"
REPO="your-repo"
TOKEN="your-github-token"

# Priority labels
gh label create "priority: critical" -c d73a4a -d "P0 - Critical priority" -R $OWNER/$REPO
gh label create "priority: high" -c ff6b6b -d "P1 - High priority" -R $OWNER/$REPO
gh label create "priority: medium" -c ffd93d -d "P2 - Medium priority" -R $OWNER/$REPO
gh label create "priority: low" -c 6bcf7f -d "P3 - Low priority" -R $OWNER/$REPO

# Type labels
gh label create "type: feature" -c a2eeef -d "New feature" -R $OWNER/$REPO
gh label create "type: bug" -c d73a4a -d "Bug fix" -R $OWNER/$REPO
# ... 添加更多标签
```

---

## 🚨 常见问题

### Q1: Actions 运行失败
**A:** 检查 Secrets 配置、查看运行日志、确认语法正确

### Q2: 标签未自动添加
**A:** 确认标签已创建、检查配置文件、查看 Actions 日志

### Q3: 项目看板未更新
**A:** 确认 PROJECT_TOKEN 配置正确、检查 token 权限

### Q4: Dependabot 未创建 PR
**A:** 检查 Dependabot 是否启用、查看 dependabot.yml 配置

---

## 📞 获取帮助

- 📖 查看 [GITHUB_ACTIONS_GUIDE.md](GITHUB_ACTIONS_GUIDE.md)
- 🐛 在项目中创建 Issue
- 💬 联系项目维护者

---

**检查完成日期**: __________
**配置人员**: __________
**状态**: ⬜ 进行中  ⬜ 已完成

---

最后更新: 2025-11-07
