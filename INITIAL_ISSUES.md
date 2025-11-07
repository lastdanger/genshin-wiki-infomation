# 初始项目任务清单

根据当前项目进度生成的初始 Issues 列表。

## 📊 当前项目状态分析

### ✅ 已完成的工作

**后端 (Backend):**
- ✅ FastAPI 基础架构已搭建
- ✅ 数据库模型已定义 (Characters, Weapons, Artifacts, Monsters)
- ✅ API 路由已创建 (7个模块)
- ✅ 中间件配置完成 (CORS, Security)
- ✅ 数据库迁移工具 (Alembic) 已配置
- ✅ 示例数据脚本已创建
- ✅ 配置管理 (config.py) 已实现

**前端 (Frontend):**
- ✅ React 应用已初始化
- ✅ 基础组件已创建
- ✅ 页面结构已搭建
- ✅ API 服务层已创建
- ✅ 构建配置完成

**基础设施:**
- ✅ Docker 配置文件已创建
- ✅ 环境变量模板已准备
- ✅ GitHub Projects 自动化已配置
- ✅ Issue 和 PR 模板已创建

### 🚧 待完成的工作

**优先级 P0-P1 (必须完成):**
1. CI/CD 流水线配置
2. 后端单元测试
3. 前端单元测试
4. API 文档生成
5. 错误处理完善
6. 数据爬虫实现

**优先级 P2-P3 (后续完善):**
1. 性能优化
2. 缓存策略实现
3. 图片上传功能
4. 搜索功能增强
5. SEO 优化
6. 部署自动化

---

## 📋 初始 Issues 列表

### Phase 0: 基础设施完善 (Sprint 1 - Week 1)

#### Issue 1: [P0][Infrastructure] 配置 CI/CD 流水线

**标题:** `[Infrastructure] Setup CI/CD pipeline with GitHub Actions`

**描述:**
```markdown
## 目标
配置完整的 CI/CD 流水线，自动化测试、代码检查和部署流程。

## 任务清单

### Backend CI
- [ ] 创建 `.github/workflows/backend-ci.yml`
- [ ] 配置 Python 环境 (3.11+)
- [ ] 配置 PostgreSQL 和 Redis 服务
- [ ] 运行代码格式检查 (Black, Flake8)
- [ ] 运行类型检查 (MyPy)
- [ ] 运行单元测试 (Pytest)
- [ ] 生成测试覆盖率报告
- [ ] 上传到 Codecov

### Frontend CI
- [ ] 创建 `.github/workflows/frontend-ci.yml`
- [ ] 配置 Node.js 环境 (18+)
- [ ] 运行 ESLint 检查
- [ ] 运行 Prettier 格式检查
- [ ] 运行单元测试 (Jest)
- [ ] 生成测试覆盖率报告
- [ ] 运行生产构建测试

### Docker Build
- [ ] 创建 `.github/workflows/docker-build.yml`
- [ ] 配置 Docker 镜像构建
- [ ] 推送到容器仓库 (可选)

## 验收标准
- [ ] 所有 PR 自动触发 CI 检查
- [ ] CI 失败时阻止合并
- [ ] 测试覆盖率达到 80% (backend) 和 70% (frontend)
- [ ] 构建时间控制在 5 分钟内

## 参考
- 已有模板在 PROJECT_BOARD_SETUP.md
- GitHub Actions 文档: https://docs.github.com/en/actions
```

**字段设置:**
- Priority: 🔥 P0 - Critical
- Module: 🔧 Infrastructure
- Type: ✨ Feature
- Estimate: 8
- Sprint: Sprint 1

---

#### Issue 2: [P1][Backend] 实现后端单元测试

**标题:** `[Backend] Implement comprehensive backend unit tests`

**描述:**
```markdown
## 目标
为后端 API 和服务添加完整的单元测试，确保代码质量和可靠性。

## 当前状态
- 后端代码已实现但缺少测试
- 已有 pytest 配置文件

## 任务清单

### API 端点测试
- [ ] 测试 Health Check API
- [ ] 测试 Characters API (CRUD)
- [ ] 测试 Weapons API (CRUD)
- [ ] 测试 Artifacts API (CRUD)
- [ ] 测试 Monsters API (CRUD)
- [ ] 测试 Game Mechanics API
- [ ] 测试 Images API
- [ ] 测试 Search API

### 服务层测试
- [ ] 测试 CharacterService
- [ ] 测试 WeaponService
- [ ] 测试 ArtifactService
- [ ] 测试 MonsterService

### 数据库测试
- [ ] 配置测试数据库
- [ ] 实现 fixture 工厂
- [ ] 测试数据库模型
- [ ] 测试数据库迁移

### 中间件测试
- [ ] 测试 CORS 中间件
- [ ] 测试 Security 中间件
- [ ] 测试错误处理中间件

## 验收标准
- [ ] 代码覆盖率 ≥ 80%
- [ ] 所有 API 端点都有测试
- [ ] 所有测试用例通过
- [ ] 测试文档清晰完整

## 技术栈
- pytest
- pytest-asyncio
- pytest-cov
- httpx (for async client testing)
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: ⚙️ Backend
- Type: 🧪 Test
- Estimate: 13
- Sprint: Sprint 1

---

#### Issue 3: [P1][Frontend] 实现前端单元测试

**标题:** `[Frontend] Implement comprehensive frontend unit tests`

**描述:**
```markdown
## 目标
为前端组件和服务添加完整的单元测试。

## 当前状态
- React 组件已实现但缺少测试
- 已有 Jest 和 React Testing Library 配置

## 任务清单

### 组件测试
- [ ] 测试 Navigation 组件
- [ ] 测试 CharacterCard 组件
- [ ] 测试 WeaponCard 组件
- [ ] 测试 ArtifactCard 组件
- [ ] 测试 SearchBar 组件
- [ ] 测试 ErrorBoundary 组件
- [ ] 测试 Loading 组件

### 页面测试
- [ ] 测试 HomePage
- [ ] 测试 CharacterListPage
- [ ] 测试 CharacterDetailPage
- [ ] 测试 WeaponListPage
- [ ] 测试 ArtifactListPage
- [ ] 测试 NotFoundPage

### API 服务测试
- [ ] 测试 CharacterService
- [ ] 测试 WeaponService
- [ ] 测试 ArtifactService
- [ ] 测试 API 错误处理
- [ ] 测试 API 拦截器

### 工具函数测试
- [ ] 测试 formatters
- [ ] 测试 validators
- [ ] 测试 helpers

## 验收标准
- [ ] 代码覆盖率 ≥ 70%
- [ ] 所有核心组件都有测试
- [ ] 所有测试用例通过
- [ ] 快照测试配置完成

## 技术栈
- Jest
- React Testing Library
- @testing-library/user-event
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: 🎨 Frontend
- Type: 🧪 Test
- Estimate: 13
- Sprint: Sprint 1

---

### Phase 1: 核心功能完善 (Sprint 1 - Week 2)

#### Issue 4: [P1][Backend] 完善 API 错误处理

**标题:** `[Backend] Implement comprehensive API error handling`

**描述:**
```markdown
## 目标
实现统一的错误处理机制，提供友好的错误响应。

## 问题
- 当前错误处理不够完善
- 缺少统一的错误响应格式
- 没有错误日志记录

## 任务清单

### 错误分类
- [ ] 定义错误类型枚举
  - ValidationError (400)
  - AuthenticationError (401)
  - AuthorizationError (403)
  - NotFoundError (404)
  - ConflictError (409)
  - InternalServerError (500)

### 错误处理器
- [ ] 实现全局异常处理器
- [ ] 实现 ValidationError 处理器
- [ ] 实现 DatabaseError 处理器
- [ ] 实现 ExternalAPIError 处理器

### 错误响应格式
- [ ] 定义统一的错误响应 Schema
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [...],
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/characters"
  }
}
```

### 错误日志
- [ ] 配置 structlog
- [ ] 记录所有 500 错误
- [ ] 记录 API 调用失败
- [ ] 添加错误追踪 ID

### 文档
- [ ] 更新 API 文档的错误响应部分
- [ ] 添加常见错误示例

## 验收标准
- [ ] 所有 API 端点返回统一格式的错误
- [ ] 错误信息清晰易懂
- [ ] 错误日志完整记录
- [ ] 不暴露敏感信息

## 参考
- spec.md 中的 FR-012 要求
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: ⚙️ Backend
- Type: 📈 Enhancement
- Estimate: 5
- Sprint: Sprint 1

---

#### Issue 5: [P1][Frontend] 实现统一错误处理和 ErrorBoundary

**标题:** `[Frontend] Implement unified error handling and ErrorBoundary`

**描述:**
```markdown
## 目标
实现前端统一错误处理机制和全局 ErrorBoundary。

## 问题
- 当前缺少统一的错误处理
- 没有 ErrorBoundary 组件
- 用户体验不友好

## 任务清单

### ErrorBoundary 组件
- [ ] 创建 ErrorBoundary 组件
- [ ] 设计错误展示 UI
- [ ] 实现错误日志上报
- [ ] 添加重试机制
- [ ] 添加返回首页功能

### API 错误处理
- [ ] 完善 Axios 拦截器
- [ ] 实现网络错误处理 (NetworkError)
- [ ] 实现业务错误处理 (BusinessError)
- [ ] 实现系统错误处理 (SystemError)
- [ ] 添加错误提示组件 (Toast/Notification)

### 错误分类
```javascript
class APIError {
  NetworkError: 网络连接失败
  TimeoutError: 请求超时
  ValidationError: 数据验证失败
  AuthError: 认证失败
  ServerError: 服务器错误
}
```

### 用户友好提示
- [ ] 网络错误: "网络连接失败，请检查网络设置"
- [ ] 超时错误: "请求超时，请重试"
- [ ] 404 错误: "请求的资源不存在"
- [ ] 500 错误: "服务器错误，我们正在处理"

### 错误日志
- [ ] 记录到浏览器 Console
- [ ] 可选：上报到错误监控服务

## 验收标准
- [ ] 应用崩溃时显示友好错误页面
- [ ] 所有 API 错误都有友好提示
- [ ] 用户可以从错误中恢复
- [ ] 错误信息不暴露技术细节

## 参考
- spec.md 中的用户故事7 (FR-013)
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: 🎨 Frontend
- Type: 📈 Enhancement
- Estimate: 5
- Sprint: Sprint 1

---

#### Issue 6: [P1][Backend] 生成 API 文档

**标题:** `[Backend] Generate and enhance API documentation with Swagger/OpenAPI`

**描述:**
```markdown
## 目标
完善 API 文档，使用 Swagger UI 提供交互式文档。

## 当前状态
- FastAPI 已自动生成基础文档
- 需要添加详细的描述和示例

## 任务清单

### API 文档增强
- [ ] 为每个端点添加详细描述
- [ ] 添加请求示例
- [ ] 添加响应示例
- [ ] 添加错误响应示例
- [ ] 添加参数说明

### Schema 文档
- [ ] 完善 Pydantic Model 的 docstring
- [ ] 添加字段示例和说明
- [ ] 添加数据验证规则说明

### 文档页面定制
- [ ] 自定义 Swagger UI 主题
- [ ] 添加项目介绍
- [ ] 添加认证说明 (如果需要)
- [ ] 添加使用指南

### 文档访问
- [ ] 开发环境: http://localhost:8002/docs
- [ ] 生产环境: https://api.genshin-wiki.com/docs

## 示例
```python
@router.get(
    "/characters/{character_id}",
    response_model=CharacterDetailSchema,
    summary="获取角色详情",
    description="根据角色 ID 获取角色的完整信息，包括属性、技能、天赋等",
    responses={
        200: {
            "description": "成功返回角色详情",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "钟离",
                        "element": "岩",
                        ...
                    }
                }
            }
        },
        404: {"description": "角色不存在"}
    }
)
```

## 验收标准
- [ ] 所有端点都有完整文档
- [ ] 文档包含请求和响应示例
- [ ] Swagger UI 可以直接测试 API
- [ ] 文档易于理解和使用

## 技术栈
- FastAPI 内置 OpenAPI 支持
- Swagger UI
- ReDoc (可选的替代文档界面)
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: ⚙️ Backend
- Type: 📝 Documentation
- Estimate: 5
- Sprint: Sprint 1

---

### Phase 2: 数据采集 (Sprint 2)

#### Issue 7: [P1][Backend] 实现角色数据爬虫

**标题:** `[Backend] Implement character data web scraper`

**描述:**
```markdown
## 目标
实现角色数据爬虫，从米游社 Wiki 和玉衡杯数据库获取角色信息。

## 数据源
- 米游社原神 Wiki: https://wiki.biligame.com/ys/首页
- 玉衡杯数据库: https://homdgcat.wiki/gi/char

## 任务清单

### 基础爬虫框架
- [ ] 创建 `src/scrapers/base_scraper.py`
- [ ] 实现请求重试机制
- [ ] 实现请求速率限制
- [ ] 添加 User-Agent 轮换

### 角色列表爬虫
- [ ] 创建 `src/scrapers/character_scraper.py`
- [ ] 爬取角色列表 (名称、星级、元素、武器类型)
- [ ] 数据清洗和标准化

### 角色详情爬虫
- [ ] 爬取基础属性 (生命值、攻击力、防御力)
- [ ] 爬取技能信息 (普通攻击、元素战技、元素爆发)
- [ ] 爬取天赋信息
- [ ] 爬取突破材料
- [ ] 爬取命之座信息

### 数据存储
- [ ] 将爬取的数据存入数据库
- [ ] 实现增量更新机制
- [ ] 处理重复数据

### 定时任务
- [ ] 使用 Celery 配置定时爬取
- [ ] 每日凌晨自动更新
- [ ] 添加手动触发接口

### 错误处理
- [ ] 网络错误处理和重试
- [ ] 解析错误处理
- [ ] 日志记录

## 技术栈
- aiohttp (异步 HTTP 请求)
- BeautifulSoup4 (HTML 解析)
- lxml (XML/HTML 解析)
- Celery (定时任务)
- Redis (任务队列)

## 验收标准
- [ ] 能够成功爬取所有角色数据
- [ ] 数据准确率 > 95%
- [ ] 爬虫运行稳定不会被封禁
- [ ] 数据自动更新功能正常

## 注意事项
- 遵守 robots.txt
- 设置合理的请求间隔
- 添加友好的 User-Agent
- 不对目标网站造成压力
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: ⚙️ Backend
- Type: ✨ Feature
- Estimate: 13
- Sprint: Sprint 2

---

#### Issue 8: [P2][Backend] 实现武器和圣遗物数据爬虫

**标题:** `[Backend] Implement weapons and artifacts data scraper`

**描述:**
```markdown
## 目标
实现武器和圣遗物数据爬虫。

## 任务清单

### 武器爬虫
- [ ] 爬取武器列表
- [ ] 爬取武器详情 (属性、特效)
- [ ] 爬取精炼信息
- [ ] 爬取获取途径

### 圣遗物爬虫
- [ ] 爬取圣遗物套装列表
- [ ] 爬取套装效果
- [ ] 爬取推荐角色
- [ ] 爬取词条推荐

### 数据存储和更新
- [ ] 存入数据库
- [ ] 定时更新

## 验收标准
- [ ] 武器数据完整准确
- [ ] 圣遗物数据完整准确
- [ ] 自动更新功能正常
```

**字段设置:**
- Priority: 🟡 P2 - Medium
- Module: ⚙️ Backend
- Type: ✨ Feature
- Estimate: 13
- Sprint: Sprint 2

---

### Phase 3: 功能增强 (Sprint 3)

#### Issue 9: [P2][Frontend] 优化角色详情页面

**标题:** `[Frontend] Enhance character detail page with talents and materials`

**描述:**
```markdown
## 目标
完善角色详情页面，添加天赋关系图和材料信息。

## 任务清单

### 天赋关系图
- [ ] 设计天赋关系图 UI
- [ ] 使用图表库实现 (推荐: React Flow 或 D3.js)
- [ ] 显示天赋升级路径
- [ ] 显示天赋之间的关系

### 材料展示
- [ ] 显示突破材料
- [ ] 显示天赋升级材料
- [ ] 添加材料来源提示
- [ ] 添加材料计算器

### 推荐配装
- [ ] 显示推荐武器
- [ ] 显示推荐圣遗物
- [ ] 显示词条优先级

### 性能优化
- [ ] 图片懒加载
- [ ] 数据缓存
- [ ] 骨架屏加载

## 验收标准
- [ ] 页面信息完整易懂
- [ ] 加载速度 < 2秒
- [ ] 移动端适配良好
```

**字段设置:**
- Priority: 🟡 P2 - Medium
- Module: 🎨 Frontend
- Type: 📈 Enhancement
- Estimate: 8
- Sprint: Sprint 3

---

#### Issue 10: [P2][Backend] 实现 Redis 缓存策略

**标题:** `[Backend] Implement Redis caching strategy`

**描述:**
```markdown
## 目标
实现 Redis 缓存，提升 API 响应速度。

## 任务清单

### 缓存配置
- [ ] 配置 Redis 连接
- [ ] 实现缓存装饰器
- [ ] 设置缓存过期时间策略

### 缓存应用
- [ ] 角色列表缓存 (5分钟)
- [ ] 角色详情缓存 (10分钟)
- [ ] 武器列表缓存 (5分钟)
- [ ] 圣遗物列表缓存 (10分钟)
- [ ] 搜索结果缓存 (3分钟)

### 缓存失效
- [ ] 实现数据更新时的缓存清除
- [ ] 实现手动清除缓存接口

### 监控
- [ ] 添加缓存命中率监控
- [ ] 添加缓存性能指标

## 验收标准
- [ ] API 响应时间减少 50%
- [ ] 缓存命中率 > 80%
- [ ] 缓存逻辑正确无误
```

**字段设置:**
- Priority: 🟡 P2 - Medium
- Module: ⚙️ Backend
- Type: 🚀 Performance
- Estimate: 5
- Sprint: Sprint 3

---

### Phase 4: 部署和运维 (Sprint 4)

#### Issue 11: [P1][Infrastructure] 配置生产环境部署

**标题:** `[Infrastructure] Setup production deployment with Docker Compose`

**描述:**
```markdown
## 目标
配置生产环境部署流程。

## 任务清单

### 环境配置
- [ ] 准备生产服务器 (VPS/云服务器)
- [ ] 配置域名和 SSL 证书
- [ ] 配置防火墙规则

### Docker 部署
- [ ] 优化 Dockerfile (多阶段构建)
- [ ] 配置 docker-compose.prod.yml
- [ ] 配置 Nginx 反向代理
- [ ] 配置 PostgreSQL 持久化
- [ ] 配置 Redis 持久化

### CI/CD 部署
- [ ] 配置自动部署工作流
- [ ] 实现蓝绿部署或滚动更新
- [ ] 配置健康检查

### 监控和日志
- [ ] 配置应用监控
- [ ] 配置日志收集
- [ ] 配置告警通知

## 验收标准
- [ ] 应用可以稳定运行
- [ ] 支持零停机更新
- [ ] 监控和日志正常
```

**字段设置:**
- Priority: 🔴 P1 - High
- Module: 🔧 Infrastructure
- Type: ✨ Feature
- Estimate: 13
- Sprint: Sprint 4

---

#### Issue 12: [P3][Documentation] 完善项目文档

**标题:** `[Documentation] Complete project documentation (README, API docs, deployment guide)`

**描述:**
```markdown
## 目标
完善项目所有文档。

## 任务清单

### README.md
- [ ] 项目介绍
- [ ] 功能特性
- [ ] 技术栈说明
- [ ] 快速开始指南
- [ ] 开发指南
- [ ] 贡献指南
- [ ] 许可证信息

### 开发文档
- [ ] 架构设计文档
- [ ] 数据库 Schema 文档
- [ ] API 设计文档
- [ ] 前端组件文档

### 部署文档
- [ ] 本地开发环境搭建
- [ ] 生产环境部署指南
- [ ] 常见问题 FAQ

### CHANGELOG
- [ ] 版本更新记录
- [ ] 功能变更说明

## 验收标准
- [ ] 文档完整清晰
- [ ] 新成员可以根据文档快速上手
```

**字段设置:**
- Priority: 🟢 P3 - Low
- Module: 📝 Documentation
- Type: 📝 Documentation
- Estimate: 5
- Sprint: Sprint 4

---

## 📊 任务优先级汇总

### Sprint 1 (2025-11-08 ~ 2025-11-21)
**主题:** 基础设施和测试完善

| Issue | Priority | Estimate | 累计 |
|-------|----------|----------|------|
| #1 CI/CD 流水线 | P0 | 8 | 8 |
| #2 后端单元测试 | P1 | 13 | 21 |
| #3 前端单元测试 | P1 | 13 | 34 |
| #4 后端错误处理 | P1 | 5 | 39 |
| #5 前端错误处理 | P1 | 5 | 44 |
| #6 API 文档生成 | P1 | 5 | 49 |

**总计:** 49 points (建议目标: 30-40 points)

### Sprint 2 (2025-11-22 ~ 2025-12-05)
**主题:** 数据采集和功能完善

| Issue | Priority | Estimate |
|-------|----------|----------|
| #7 角色数据爬虫 | P1 | 13 |
| #8 武器圣遗物爬虫 | P2 | 13 |

### Sprint 3 (2025-12-06 ~ 2025-12-19)
**主题:** 功能增强和性能优化

| Issue | Priority | Estimate |
|-------|----------|----------|
| #9 角色详情页优化 | P2 | 8 |
| #10 Redis 缓存 | P2 | 5 |

### Sprint 4 (2025-12-20 ~ 2026-01-02)
**主题:** 部署和文档

| Issue | Priority | Estimate |
|-------|----------|----------|
| #11 生产环境部署 | P1 | 13 |
| #12 完善项目文档 | P3 | 5 |

---

## 🎯 建议的执行策略

### Week 1 重点
1. 配置 CI/CD 流水线 (#1)
2. 实现后端错误处理 (#4)
3. 开始后端单元测试 (#2)

### Week 2 重点
1. 完成后端单元测试 (#2)
2. 实现前端错误处理 (#5)
3. 开始前端单元测试 (#3)
4. 生成 API 文档 (#6)

---

## 📝 创建 Issue 的步骤

1. 访问 GitHub 仓库的 Issues 页面
2. 点击 "New issue"
3. 选择合适的模板 (Feature Request)
4. 复制上面对应的内容
5. 设置 Labels、Priority、Module、Type、Estimate
6. 添加到 Projects
7. Submit issue

---

## 💡 提示

- 所有 Issue 会自动添加到项目看板的 Backlog
- 在 Sprint Planning 时将任务移到 Ready
- 分配任务后自动移到 In Progress
- 完成并合并 PR 后自动移到 Done

---

最后更新: 2025-11-07
