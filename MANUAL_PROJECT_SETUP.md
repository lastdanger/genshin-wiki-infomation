# 手动项目设置指南

## 问题说明

GitHub Actions 的 `auto-add-to-project` 工作流失败，错误信息：
```
Could not resolve to a ProjectV2 with the number 2
```

这通常是因为项目 URL 格式不正确或权限问题。

---

## 🎯 推荐的解决方案

### 方案 A: 手动添加 Issue 到项目（最可靠）

虽然不能自动添加，但 **Projects Workflows 仍然可以自动管理状态**。

#### 操作步骤：

1. **创建新 Issue**
   - 在仓库中点击 **Issues** → **New issue**
   - 填写 Issue 内容

2. **手动添加到项目**
   - 在 Issue 页面右侧找到 **Projects**
   - 点击齿轮图标 ⚙️
   - 选择 **"Genshin Wiki Info - Development"**
   - ✅ Issue 会自动进入 **Backlog** 列（由 Projects Workflows 自动设置）

3. **后续自动化仍然有效**
   - Issue 关闭 → 自动移到 Done ✅
   - PR 审批通过 → 自动移到 Testing ✅
   - PR 合并 → 自动移到 Done ✅

---

### 方案 B: 修复 GitHub Actions 工作流

#### Step 1: 检查项目类型

打开项目看板，查看 URL 格式：

**如果是用户级项目：**
```
https://github.com/users/lastdanger/projects/2
```

**如果是组织级项目：**
```
https://github.com/orgs/YOUR_ORG/projects/2
```

**如果是仓库级项目（Classic）：**
```
https://github.com/lastdanger/genshin-wiki-infomation/projects/2
```

> ⚠️ 注意：新版 Projects (Beta) 和旧版 Projects (Classic) 是不同的！
>
> - **Projects (Beta)** ✅ - URL 包含 `/users/` 或 `/orgs/`，支持自动化
> - **Projects (Classic)** ❌ - URL 格式为 `/repos/.../projects/`，不支持新自动化

#### Step 2: 验证项目是 Projects (Beta)

**特征：**
- ✅ 有 "Workflows" 标签
- ✅ 可以添加自定义字段
- ✅ 支持多视图（Board, Table, Roadmap）
- ✅ URL 格式：`/users/USERNAME/projects/NUMBER` 或 `/orgs/ORG/projects/NUMBER`

**如果是 Projects (Classic)：**
- 需要创建新的 Projects (Beta)
- 或者禁用自动添加工作流，手动管理

#### Step 3: 配置 Actions 权限

进入仓库 **Settings** → **Actions** → **General**：

1. 滚动到 **Workflow permissions**
2. 选择 **"Read and write permissions"** ✅
3. 勾选 **"Allow GitHub Actions to create and approve pull requests"** ✅
4. 点击 **Save**

#### Step 4: 创建 Personal Access Token (如果需要)

如果标准 `GITHUB_TOKEN` 权限不足，需要创建 PAT：

1. 进入 **GitHub Settings** → **Developer settings** → **Personal access tokens** → **Tokens (classic)**
2. 点击 **Generate new token** → **Generate new token (classic)**
3. 选择权限：
   - ✅ `repo` (Full control of private repositories)
   - ✅ `project` (Full control of projects)
   - ✅ `read:org` (Read org and team membership)
4. 点击 **Generate token**
5. 复制 token

6. 进入仓库 **Settings** → **Secrets and variables** → **Actions**
7. 点击 **New repository secret**
8. Name: `PROJECT_TOKEN`
9. Value: 粘贴刚才的 token
10. 点击 **Add secret**

11. 修改工作流文件，使用新 token：
```yaml
github-token: ${{ secrets.PROJECT_TOKEN }}
```

---

### 方案 C: 使用替代工作流

使用 GitHub GraphQL API 直接操作：

```yaml
name: Auto Add to Project (GraphQL)

on:
  issues:
    types: [opened]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - name: Get project data
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          ISSUE_ID: ${{ github.event.issue.node_id }}
        run: |
          gh api graphql -f query='
            query {
              user(login: "lastdanger") {
                projectsV2(first: 10) {
                  nodes {
                    id
                    title
                    number
                  }
                }
              }
            }'
```

---

## 🎯 推荐的工作流程

根据目前的情况，我推荐使用 **方案 A（手动添加 Issue）**：

### 优势：

1. ✅ **简单可靠** - 不依赖复杂的权限配置
2. ✅ **自动化仍然有效** - Projects Workflows 会自动管理状态转换
3. ✅ **只需要一次手动操作** - 创建 Issue 时手动添加到项目
4. ✅ **不影响团队协作** - 团队成员可以快速上手

### 操作流程：

```
1. 创建 Issue
   ↓
2. 手动添加到项目（右侧 Projects 菜单）
   ↓
3. ✅ 自动进入 Backlog（Projects Workflow）
   ↓
4. 后续所有状态转换都自动化
   - 分配 → In Progress
   - 关闭 → Done
   - PR 合并 → Done
   - 等等
```

---

## 📝 创建 Issue 的最佳实践

### 使用 Issue 模板

我们已经创建了 4 个 Issue 模板：

1. **🐛 Bug 报告** - 用于报告 Bug
2. **✨ 功能请求** - 用于提出新功能
3. **🔄 数据更新请求** - 用于游戏数据更新
4. **📝 文档改进** - 用于文档相关

### 创建 Issue 时的检查清单：

- [ ] 选择合适的模板
- [ ] 填写清晰的标题
- [ ] 提供详细的描述
- [ ] 添加相关的 Labels
- [ ] **添加到 Projects**（重要！）
- [ ] 设置 Priority、Module 等自定义字段（在项目看板中）

---

## 🔧 如果仍想修复自动添加

### 调试步骤：

1. **确认项目 URL**
   - 打开项目看板
   - 复制浏览器地址栏的完整 URL
   - 确认是 `/users/` 还是 `/orgs/` 格式

2. **查看 Actions 日志**
   - 进入 **Actions** 标签
   - 点击失败的工作流运行
   - 查看详细错误信息

3. **尝试不同的 URL 格式**
   ```yaml
   # 格式 1: 用户级
   project-url: https://github.com/users/lastdanger/projects/2

   # 格式 2: 组织级（如果适用）
   project-url: https://github.com/orgs/YOUR_ORG/projects/2
   ```

4. **检查项目编号**
   - 可能项目编号不是 2
   - 尝试 1, 3 等其他编号

---

## 📚 相关文档

- [GitHub Projects 文档](https://docs.github.com/en/issues/planning-and-tracking-with-projects)
- [actions/add-to-project 文档](https://github.com/actions/add-to-project)
- [GitHub Actions 权限](https://docs.github.com/en/actions/security-guides/automatic-token-authentication)

---

## 💡 总结

**最快的解决方案：**

1. 暂时接受手动添加 Issue 到项目
2. 享受其他所有的自动化功能
3. 未来有时间时再调试 GitHub Actions

**记住：**
- ✅ Projects Workflows（状态自动化）仍然完全有效
- ✅ 只是创建时需要手动点击一下添加到项目
- ✅ 这并不影响项目管理的效率

---

最后更新：2025-11-07
