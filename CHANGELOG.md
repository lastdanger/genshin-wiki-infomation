# Changelog

本文档记录项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 计划中
- 角色、武器、圣遗物数据爬虫
- 完善角色详情页面展示
- 生产环境 Docker 部署
- 性能监控和优化

---

## [0.3.0] - 2025-11-10

### Added
- ✨ 实现前端单元测试框架
  - ErrorBoundary 组件测试（100% 覆盖率）
  - Toast 组件测试（100% 覆盖率）
  - useErrorHandler Hook 测试
  - ErrorHandler 工具测试（96% 覆盖率）
  - Axios 拦截器测试（76% 覆盖率）
- 📝 完善项目文档
  - 更新主 README.md，添加详细说明和徽章
  - 创建开发指南（DEVELOPMENT.md）
  - 创建更新日志（CHANGELOG.md）

### Changed
- 🔧 配置 Jest 测试环境
- 📦 安装 axios-mock-adapter 测试依赖

### Fixed
- 🐛 修复 ErrorBoundary 测试中的文案匹配问题
- 🐛 修复 getUserFriendlyMessage 测试断言

---

## [0.2.0] - 2025-11-07

### Added
- ⚡ 实现 Redis 缓存策略
  - 缓存管理器（CacheManager）
  - 缓存装饰器（@cached, @cache_invalidate）
  - 缓存统计功能（hits, misses, hit rate）
  - 缓存监控 API 端点
- 📚 创建缓存策略文档
  - CACHING_STRATEGY.md - 完整的缓存设计说明
  - CACHING_EXAMPLES.md - 缓存使用示例代码
- 🔍 缓存监控 API
  - GET /api/cache/stats - 获取缓存统计
  - POST /api/cache/stats/reset - 重置统计
  - DELETE /api/cache/clear - 清除所有缓存
  - DELETE /api/cache/clear/{pattern} - 按模式清除
  - GET /api/cache/health - Redis 健康检查

### Changed
- 🎨 优化缓存键生成策略（支持哈希）
- ⚡ 定义不同数据类型的 TTL 策略（5-30分钟）

---

## [0.1.0] - 2025-11-06

### Added
- 🎉 初始化项目结构
- 🔨 后端 API 错误处理系统
  - 统一错误处理中间件
  - 标准化错误响应格式
  - 错误日志记录
  - 错误监控准备
- 🛡️ 前端错误处理系统
  - ErrorBoundary 组件
  - ErrorFallback 组件
  - Toast 提示组件
  - useErrorHandler Hook
  - Axios 拦截器
  - 统一错误处理类（ApiError）
- 📖 后端文档
  - API_USAGE_GUIDE.md - API 使用指南
  - API_EXAMPLES.md - API 示例代码
  - ERROR_HANDLING.md - 错误处理文档
- 📖 前端文档
  - ERROR_HANDLING.md - 错误处理使用文档
- 🔧 基础架构
  - FastAPI 后端框架
  - React 前端框架
  - PostgreSQL 数据库
  - Redis 缓存支持

### Changed
- 📝 更新 README.md 添加项目说明
- 🔧 配置端口（后端 8001，前端 3002）
- 🎨 优化项目目录结构

### Technical Details

#### 后端技术栈
- FastAPI 0.104+
- SQLAlchemy 2.0+
- PostgreSQL 12+
- Redis 6+
- Pydantic 2.0+

#### 前端技术栈
- React 18.2
- React Router 6.18
- Axios 1.6
- Jest + React Testing Library

---

## 版本说明

### 版本号格式：主版本号.次版本号.修订号

- **主版本号**：不兼容的 API 变更
- **次版本号**：向后兼容的功能新增
- **修订号**：向后兼容的问题修复

### 变更类型

- **Added**: 新功能
- **Changed**: 现有功能的变更
- **Deprecated**: 即将移除的功能
- **Removed**: 已移除的功能
- **Fixed**: Bug 修复
- **Security**: 安全性修复

---

## 链接

- [项目仓库](https://github.com/lastdanger/genshin-wiki-infomation)
- [问题反馈](https://github.com/lastdanger/genshin-wiki-infomation/issues)
- [Pull Requests](https://github.com/lastdanger/genshin-wiki-infomation/pulls)

---

**最后更新**: 2025-11-10
