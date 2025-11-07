# Implementation Plan: 原神游戏信息网站

**Branch**: `001-genshin-info-website` | **Date**: 2025-11-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-genshin-info-website/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

建立一个统一的原神游戏信息查询平台，整合角色、武器、圣遗物、怪物等多类型游戏数据。系统需要支持数据自动同步、图片上传管理、移动端优化，并确保用户能在3步内找到所需信息，页面加载时间控制在3秒内。

## Technical Context

**Language/Version**: Python 3.11+（用户明确指定使用Python）
**Primary Dependencies**: FastAPI + SQLAlchemy + asyncpg（基于性能和异步需求选择）
**Storage**: PostgreSQL 15+（JSONB支持、中文全文搜索、关系查询优秀）
**Testing**: pytest + pytest-asyncio（异步测试支持）
**Target Platform**: Linux服务器 + Web浏览器（移动端优化）
**Project Type**: Web应用（前端+后端分离架构）
**Performance Goals**: 页面加载<3秒，支持100并发用户，搜索响应<1秒
**Constraints**: 移动端适配，HTTPS加密，图片内容审核，24小时数据同步
**Scale/Scope**: 预期1000+活跃用户，6个主要功能模块，3个外部数据源集成

## 章程合规检查

*门控: Phase 0研究前必须通过，Phase 1设计后需要重新检查*

**用户体验检查**:
- [x] 操作流程不超过3步？（规格明确所有查询3步内完成）
- [x] 页面加载时间<3秒？（性能目标已设定）
- [x] 界面使用中文，专业词汇有释义？（目标用户为中文玩家）
- [x] 移动端适配？（明确要求移动端优化）

**数据安全检查**:
- [x] 数据传输使用HTTPS？（约束条件中已包含）
- [x] 不收集游戏账号密码？（仅展示公开游戏数据）
- [x] 符合《个人信息保护法》？（已在每个用户故事中检查）
- [x] 用户可以删除个人数据？（仅图片上传功能涉及，已确认）

**开发规范检查**:
- [x] 函数不超过50行？（开发规范要求）
- [x] 有单元测试？（使用pytest框架）
- [x] 代码注释使用中文？（章程要求）
- [x] 禁用"全面提升"等空话？（文档规范要求）

## Project Structure

### Documentation (this feature)

```text
specs/001-genshin-info-website/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/          # 数据模型（角色、武器、圣遗物等）
│   ├── services/        # 业务逻辑（数据同步、图片处理等）
│   ├── api/            # REST API接口
│   ├── scrapers/       # 数据爬取模块（wiki、数据库同步）
│   └── utils/          # 工具函数
├── tests/
│   ├── contract/       # API合约测试
│   ├── integration/    # 集成测试
│   └── unit/          # 单元测试
├── requirements.txt    # Python依赖
└── config/            # 配置文件

frontend/
├── src/
│   ├── components/     # 可复用组件
│   ├── pages/         # 页面组件（角色、武器、圣遗物等版块）
│   ├── services/      # API调用服务
│   ├── assets/        # 静态资源
│   └── styles/        # 样式文件
├── tests/
│   ├── unit/         # 组件单元测试
│   └── e2e/          # 端到端测试
└── package.json      # 前端依赖

shared/
├── types/            # 共享类型定义
└── schemas/          # 数据模型Schema
```

**Structure Decision**: 选择Web应用架构（Option 2），因为需要前后端分离以支持移动端优化和独立部署。Backend使用Python处理数据同步和API，Frontend使用现代Web技术确保移动端适配。

## Complexity Tracking

> **所有章程检查项目均已通过，无需复杂度违规解释**

本项目完全符合章程要求：
- ✅ 用户体验优先：3步内完成操作，<3秒加载时间
- ✅ 数据准确性：多源同步，99%准确率目标
- ✅ 隐私安全保护：HTTPS加密，符合法规，用户可删除数据
- ✅ 简化操作流程：移动端适配，减少用户输入
- ✅ 文档规范化：中文注释，功能文档完整

**架构决策合理性**:
- FastAPI选择基于性能需求（100并发用户）
- PostgreSQL选择基于数据特征（JSON支持、中文搜索）
- 前后端分离支持移动端优化需求

---

## 前端架构设计详解

### API Service 层设计

**设计目标**: 提供统一的HTTP请求封装，实现请求拦截、响应转换、错误处理和重试机制

**架构层次**:
```
┌─────────────────────────────────────────────────────┐
│              React Components                       │
│         (CharacterListPage, WeaponCard...)          │
└────────────────────┬────────────────────────────────┘
                     │ 调用API方法
                     ▼
┌─────────────────────────────────────────────────────┐
│           Domain API Services                       │
│  (characterAPI, weaponAPI, artifactAPI...)          │
│  - 业务方法封装（getList, getDetail, create...）     │
└────────────────────┬────────────────────────────────┘
                     │ 继承/使用
                     ▼
┌─────────────────────────────────────────────────────┐
│              BaseAPIService                         │
│  - HTTP方法封装 (get, post, put, delete)            │
│  - 请求拦截器 (添加token、日志)                      │
│  - 响应拦截器 (数据转换、错误处理)                   │
│  - 重试机制 (网络错误自动重试)                       │
└────────────────────┬────────────────────────────────┘
                     │ 使用
                     ▼
┌─────────────────────────────────────────────────────┐
│            HTTP Client (Axios)                      │
│  - 底层HTTP请求库                                   │
└─────────────────────────────────────────────────────┘
```

**核心类设计**:

1. **BaseAPIService** (`frontend/src/services/base/BaseAPIService.js`)
   - 职责: 提供HTTP请求的基础功能
   - 方法:
     - `get(url, params, config)`: GET请求
     - `post(url, data, config)`: POST请求
     - `put(url, data, config)`: PUT请求
     - `delete(url, config)`: DELETE请求
     - `request(config)`: 通用请求方法
   - 特性:
     - 自动添加baseURL
     - 请求超时控制
     - 请求取消支持
     - 请求日志记录

2. **RequestInterceptor** (`frontend/src/services/base/interceptors.js`)
   - 职责: 请求前的统一处理
   - 功能:
     - 添加认证token（如果需要）
     - 添加请求ID（用于追踪）
     - 添加时间戳
     - 请求日志记录
     - 请求参数序列化

3. **ResponseInterceptor** (`frontend/src/services/base/interceptors.js`)
   - 职责: 响应后的统一处理
   - 功能:
     - 统一响应格式转换
     - 错误分类处理
     - 业务错误提取
     - 响应日志记录
     - Token刷新处理

4. **Domain API Services** (如 `frontend/src/services/characterAPI.js`)
   - 职责: 封装特定业务领域的API调用
   - 示例方法:
     - `getCharacterList(filters)`: 获取角色列表
     - `getCharacterDetail(id)`: 获取角色详情
     - `searchCharacters(query)`: 搜索角色
     - `getCharacterFilters()`: 获取筛选选项
     - `createCharacter(data)`: 创建角色（管理功能）
     - `updateCharacter(id, data)`: 更新角色
     - `deleteCharacter(id)`: 删除角色

**API响应统一格式**:
```javascript
// 成功响应
{
  success: true,
  data: {
    // 实际数据
    characters: [...],
    total: 100,
    page: 1,
    pages: 10
  },
  message: "操作成功",
  timestamp: "2025-11-06T12:00:00Z",
  requestId: "req-123456"
}

// 错误响应
{
  success: false,
  error: {
    code: "VALIDATION_ERROR",
    message: "请求参数验证失败",
    details: {
      "name": "角色名称不能为空"
    }
  },
  timestamp: "2025-11-06T12:00:00Z",
  requestId: "req-123456"
}
```

---

### 统一错误处理机制

**设计目标**: 提供分层的错误处理，确保用户体验和系统稳定性

**错误分类体系**:

1. **NetworkError** (网络错误)
   - 触发条件:
     - 网络连接失败
     - 请求超时
     - DNS解析失败
   - 处理策略:
     - 自动重试（最多3次）
     - 显示网络错误提示
     - 提供"重试"按钮
   - 用户提示: "网络连接失败，请检查网络设置"

2. **BusinessError** (业务错误)
   - 触发条件:
     - HTTP 4xx状态码
     - 服务器返回业务错误
   - 子类型:
     - ValidationError (400): 参数验证失败
     - AuthenticationError (401): 认证失败
     - PermissionError (403): 权限不足
     - NotFoundError (404): 资源不存在
     - ConflictError (409): 资源冲突
   - 处理策略:
     - 不自动重试
     - 显示具体错误信息
     - 引导用户修正
   - 用户提示: 根据具体错误显示详细信息

3. **SystemError** (系统错误)
   - 触发条件:
     - HTTP 5xx状态码
     - 服务器内部错误
     - 未知错误
   - 处理策略:
     - 记录错误日志
     - 显示通用错误页面
     - 不暴露技术细节
   - 用户提示: "系统繁忙，请稍后重试"

**错误处理流程**:
```
API请求发起
    │
    ▼
请求拦截器处理
    │
    ▼
发送HTTP请求
    │
    ├─成功─► 响应拦截器 ─► 数据转换 ─► 返回给组件
    │
    └─失败─► 错误拦截器
              │
              ├─► 网络错误？ ──Yes─► 自动重试
              │                      │
              │                      └─► 重试失败？
              │                          │
              │                          ├─Yes─► 显示网络错误 + 重试按钮
              │                          └─No──► 返回成功
              │
              ├─► 业务错误(4xx)？ ──Yes─► 提取错误信息 ─► 抛出BusinessError
              │
              └─► 系统错误(5xx)？ ──Yes─► 记录日志 ─► 抛出SystemError
```

**错误边界组件设计**:

1. **全局错误边界** (`frontend/src/components/ErrorBoundary/GlobalErrorBoundary.jsx`)
   - 位置: App根组件
   - 捕获: 所有未捕获的JavaScript错误
   - 显示: 友好的错误页面
   - 功能:
     - 错误信息记录
     - 提供"返回首页"按钮
     - 提供"报告问题"功能

2. **局部错误边界** (`frontend/src/components/ErrorBoundary/ErrorBoundary.jsx`)
   - 位置: 关键组件外层
   - 捕获: 特定组件树的错误
   - 显示: 降级UI或错误提示
   - 功能:
     - 组件级错误隔离
     - 不影响其他组件
     - 提供重试功能

**错误日志服务** (`frontend/src/services/logger/ErrorLogger.js`):
- 功能:
  - 本地日志记录（localStorage/IndexedDB）
  - 远程日志上报（可选）
  - 错误统计分析
  - 用户操作轨迹记录
- 记录内容:
  - 错误类型和消息
  - 错误堆栈
  - 请求URL和参数
  - 用户操作序列
  - 浏览器和设备信息
  - 时间戳

---

### 前端目录结构更新

```
frontend/src/
├── services/
│   ├── base/                    # 基础服务层（新增）
│   │   ├── BaseAPIService.js    # API基础类
│   │   ├── interceptors.js      # 请求/响应拦截器
│   │   ├── errorHandler.js      # 错误处理器
│   │   └── retryPolicy.js       # 重试策略
│   │
│   ├── errors/                  # 错误类定义（新增）
│   │   ├── NetworkError.js      # 网络错误
│   │   ├── BusinessError.js     # 业务错误
│   │   ├── SystemError.js       # 系统错误
│   │   └── index.js             # 错误类导出
│   │
│   ├── logger/                  # 日志服务（新增）
│   │   ├── ErrorLogger.js       # 错误日志记录器
│   │   ├── RequestLogger.js     # 请求日志记录器
│   │   └── LoggerConfig.js      # 日志配置
│   │
│   ├── characterAPI.js          # 角色API服务（重构）
│   ├── weaponAPI.js             # 武器API服务（重构）
│   ├── artifactAPI.js           # 圣遗物API服务（重构）
│   ├── monsterAPI.js            # 怪物API服务（新增）
│   └── searchAPI.js             # 搜索API服务（新增）
│
├── components/
│   ├── ErrorBoundary/           # 错误边界组件（新增）
│   │   ├── GlobalErrorBoundary.jsx    # 全局错误边界
│   │   ├── ErrorBoundary.jsx          # 通用错误边界
│   │   ├── ErrorFallback.jsx          # 错误降级UI
│   │   └── ErrorBoundary.css
│   │
│   └── UI/
│       ├── ErrorMessage.jsx     # 错误提示组件（新增）
│       ├── RetryButton.jsx      # 重试按钮（新增）
│       └── LoadingSpinner.jsx   # 加载指示器
```

---

### 实施优先级

**Phase 1: 基础设施（P1 - 阻塞性）**
1. 创建BaseAPIService基类
2. 实现请求/响应拦截器
3. 定义错误类体系
4. 实现基础错误处理

**Phase 2: API服务重构（P1）**
1. 重构characterAPI使用新架构
2. 重构weaponAPI使用新架构
3. 重构artifactAPI使用新架构
4. 创建monsterAPI

**Phase 3: 错误边界和UI（P2）**
1. 实现GlobalErrorBoundary
2. 实现ErrorBoundary组件
3. 创建错误UI组件
4. 集成到现有页面

**Phase 4: 日志和监控（P3）**
1. 实现ErrorLogger
2. 添加日志上报功能
3. 错误统计分析
4. 性能监控集成

---

### 成功标准

**技术指标**:
- [ ] 所有API调用通过统一Service层
- [ ] 错误分类覆盖率100%
- [ ] 网络错误自动重试成功率>80%
- [ ] 错误日志记录率100%
- [ ] 用户可见错误提示友好度评分>4.5/5

**用户体验指标**:
- [ ] 网络错误恢复时间<5秒
- [ ] 错误提示清晰度用户调研>90%满意
- [ ] 系统错误不导致页面崩溃
- [ ] 错误发生时用户可继续使用其他功能

**代码质量指标**:
- [ ] API Service代码复用率>70%
- [ ] 错误处理逻辑集中度>90%
- [ ] 单元测试覆盖率>80%
- [ ] 代码review通过率100%
