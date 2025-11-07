# 项目字段说明 | Project Fields Guide

本文档简要说明 GitHub Projects 看板中各个自定义字段的含义和使用方法。

---

## 📋 字段列表

### 1. Status (状态) - 系统字段

任务当前所处的工作流阶段。

| 状态 | 说明 | 何时使用 |
|------|------|---------|
| 📥 Backlog | 待整理 | Issue 创建后自动进入，等待规划 |
| 🎯 Ready | 准备开发 | Sprint Planning 选中，准备分配 |
| 🔄 In Progress | 开发中 | 任务被分配后，正在开发 |
| 👀 Review | 代码审查 | PR 创建后，等待审查 |
| 🧪 Testing | 测试中 | 代码审查通过，进入测试 |
| ✅ Done | 已完成 | PR 合并或 Issue 关闭 |
| ❌ Blocked | 被阻塞 | 遇到阻碍，无法继续 |

**自动化：** 大部分状态转换由 Workflows 自动完成。

---

### 2. Priority (优先级)

任务的重要程度和紧急程度。

| 优先级 | 说明 | 示例 |
|--------|------|------|
| 🔥 P0 - Critical | 严重问题，影响系统运行 | 系统崩溃、数据丢失、安全漏洞 |
| 🔴 P1 - High | 核心功能，必须实现 | 角色列表 API、用户认证 |
| 🟡 P2 - Medium | 重要优化，提升体验 | 搜索功能、性能优化 |
| 🟢 P3 - Low | 次要功能，可延后 | UI 美化、文档完善 |

**使用建议：**
- Sprint 优先处理 P0 和 P1
- P2 根据资源情况安排
- P3 可以放入后续 Sprint

---

### 3. Module (功能模块)

任务所属的功能模块或技术领域。

| 模块 | 说明 | 负责内容 |
|------|------|---------|
| 🎭 Character | 角色模块 | 角色列表、详情、数据爬虫 |
| ⚔️ Weapon | 武器模块 | 武器列表、详情、数据爬虫 |
| 💎 Artifact | 圣遗物模块 | 圣遗物列表、详情、推荐搭配 |
| 👾 Monster | 怪物模块 | 怪物图鉴、技能机制、应对策略 |
| 📚 GameMechanic | 游戏机制 | 基础机制、进阶攻略、计算器 |
| 🖼️ Gallery | 图片管理 | 图片上传、展示、审核 |
| 🔧 Infrastructure | 基础设施 | Docker、CI/CD、部署配置 |
| 🎨 Frontend | 前端 | React 组件、页面、样式 |
| ⚙️ Backend | 后端 | API、业务逻辑、数据处理 |
| 🗄️ Database | 数据库 | Schema 设计、迁移、优化 |

**使用建议：**
- 每个 Issue 只选择一个主要模块
- 便于按模块分配任务和查看进度

---

### 4. Type (任务类型)

任务的工作性质。

| 类型 | 说明 | 示例 |
|------|------|------|
| ✨ Feature | 新功能开发 | 实现角色列表、添加搜索功能 |
| 🐛 Bug | 错误修复 | 修复页面崩溃、解决数据错误 |
| 📈 Enhancement | 功能增强 | 优化加载速度、改进 UI 交互 |
| 🔄 Refactor | 代码重构 | 重构 API 层、优化组件结构 |
| 📝 Documentation | 文档编写 | API 文档、使用指南、README |
| 🧪 Test | 测试相关 | 单元测试、集成测试、E2E 测试 |
| 🚀 Performance | 性能优化 | 缓存优化、查询优化、懒加载 |

**使用建议：**
- Bug 和 P0 Feature 优先处理
- Refactor 和 Documentation 穿插进行
- 每个 Sprint 保持类型多样性

---

### 5. Estimate (工作量估算)

完成任务需要的工作量，使用 Story Points。

| Points | 复杂度 | 时间 | 示例 |
|--------|--------|------|------|
| 1 | 非常简单 | 1-2h | 修改配置、更新文档 |
| 2 | 简单 | 2-4h | 简单组件、小功能 |
| 3 | 中等 | 4-8h | 标准 CRUD、普通页面 |
| 5 | 复杂 | 1-2天 | 复杂页面、API 设计 |
| 8 | 很复杂 | 2-3天 | 核心模块、数据爬虫 |
| 13 | 非常复杂 | 3-5天 | 大型功能、架构改动 |

**使用建议：**
- 超过 13 points 的任务应拆分
- 一个 Sprint (2周) 通常包含 20-40 points
- 估算基于团队平均能力

---

### 6. Sprint (迭代周期)

任务计划在哪个 Sprint 完成。

**配置：**
- 周期：2 周
- 开始日期：2025-11-08

**当前规划：**
```
Sprint 1 (2025-11-08 ~ 2025-11-21): 基础设施搭建
Sprint 2 (2025-11-22 ~ 2025-12-05): 核心功能开发
Sprint 3 (2025-12-06 ~ 2025-12-19): 功能完善
Sprint 4 (2025-12-20 ~ 2026-01-02): 优化和测试
```

**使用建议：**
- Sprint Planning 时分配任务到 Sprint
- 每个 Sprint 开始时设置 Sprint 字段
- 使用 "Current Sprint" 视图查看当前任务

---

### 7. Assignee (负责人) - 系统字段

任务的负责人。

**使用建议：**
- 每个任务只分配一个主要负责人
- 可以在评论中 @其他协作者
- 分配后任务自动移到 In Progress

---

### 8. Labels (标签) - 系统字段

任务的附加标记，可多选。

**推荐的 Labels：**

**优先级标签：**
- `priority: critical` - P0
- `priority: high` - P1
- `priority: medium` - P2
- `priority: low` - P3

**类型标签：**
- `type: feature`, `type: bug`, `type: enhancement`, 等

**模块标签：**
- `module: character`, `module: weapon`, 等

**状态标签：**
- `good first issue` - 适合新手
- `help wanted` - 需要帮助
- `blocked` - 被阻塞

**使用建议：**
- Labels 是补充信息，主要使用自定义字段
- 便于在 Issues 列表中快速筛选
- 可以用于触发自动化

---

## 📊 字段使用示例

### 示例 1: 新功能 Issue

```
标题: [Character] Implement character list API
Status: Backlog
Priority: 🔴 P1 - High
Module: 🎭 Character
Type: ✨ Feature
Estimate: 8
Sprint: Sprint 2
Assignee: @developer
Labels: type:feature, module:character, priority:high
```

### 示例 2: Bug 修复 Issue

```
标题: [Frontend] Fix character detail page crash
Status: In Progress
Priority: 🔥 P0 - Critical
Module: 🎨 Frontend
Type: 🐛 Bug
Estimate: 3
Sprint: Sprint 1
Assignee: @frontend-dev
Labels: type:bug, module:frontend, priority:critical
```

### 示例 3: 技术债务 Issue

```
标题: [Backend] Refactor API service layer
Status: Ready
Priority: 🟡 P2 - Medium
Module: ⚙️ Backend
Type: 🔄 Refactor
Estimate: 5
Sprint: Sprint 3
Assignee: @backend-dev
Labels: type:refactor, module:backend, priority:medium
```

---

## 🎯 快速决策指南

### 如何设置 Priority？

```
是否影响系统运行？
  ├─ 是 → 🔥 P0
  └─ 否 → 是否核心功能？
      ├─ 是 → 🔴 P1
      └─ 否 → 是否重要优化？
          ├─ 是 → 🟡 P2
          └─ 否 → 🟢 P3
```

### 如何选择 Module？

```
任务主要涉及哪个领域？
  ├─ 游戏数据相关 → Character / Weapon / Artifact / Monster
  ├─ 用户功能 → Gallery / GameMechanic
  ├─ 技术层面 → Frontend / Backend / Database
  └─ 项目基础 → Infrastructure
```

### 如何估算 Estimate？

```
任务复杂度？
  ├─ 配置级 → 1 point
  ├─ 组件级 → 2-3 points
  ├─ 页面级 → 5 points
  ├─ 模块级 → 8 points
  └─ 系统级 → 13 points (需要拆分)
```

---

## 💡 最佳实践

### 创建 Issue 时

1. ✅ **标题清晰**：`[模块] 简短描述`
2. ✅ **设置字段**：至少设置 Priority, Module, Type
3. ✅ **添加描述**：使用模板提供详细信息
4. ✅ **估算工作量**：设置 Estimate
5. ✅ **分配 Sprint**：如果已规划

### Sprint Planning 时

1. ✅ **按优先级选择**：P0 > P1 > P2 > P3
2. ✅ **平衡模块**：不要只做一个模块
3. ✅ **考虑依赖**：先做基础功能
4. ✅ **控制总量**：不超过团队容量
5. ✅ **设置 Sprint 字段**：标记当前 Sprint

### 开发过程中

1. ✅ **及时更新状态**：虽然大部分自动化，但 Blocked 需要手动
2. ✅ **记录进展**：在评论中更新进度
3. ✅ **关联 PR**：PR 描述中引用 Issue 编号
4. ✅ **调整估算**：如果发现估算不准，在评论中说明

---

## 🔗 相关文档

- [PROJECT_BOARD_SETUP.md](PROJECT_BOARD_SETUP.md) - 看板设置完整指南
- [GITHUB_SETUP_QUICKSTART.md](GITHUB_SETUP_QUICKSTART.md) - 快速启动清单
- [MANUAL_PROJECT_SETUP.md](MANUAL_PROJECT_SETUP.md) - 故障排查指南

---

## 📞 需要帮助？

如果对字段使用有疑问：
1. 查看项目看板中的示例 Issues
2. 查阅本文档的示例部分
3. 在项目 Discussions 中提问

---

最后更新：2025-11-07
