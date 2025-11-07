# Phase 0 Research: 原神游戏信息网站技术选型

## Research Overview

本研究解决技术上下文中的关键决策问题，为原神游戏信息网站选择最适合的技术栈。

## 决策1: Web框架选择

### Decision: FastAPI

### Rationale

FastAPI是本项目的最佳选择，基于以下关键因素：

1. **性能要求满足**: 原生async支持确保<3秒页面加载和100并发用户处理能力
2. **API优先架构**: 项目采用前后端分离，FastAPI的自动OpenAPI文档和类型安全完美匹配
3. **异步数据同步**: 原生async对爬取多个数据源（B站wiki、玉衡杯数据库）至关重要
4. **开发速度**: 相比Django的API开发，FastAPI减少50%的样板代码
5. **现代Python实践**: 类型提示和async/await符合团队技能发展方向

### Alternatives Considered

- **Django + DRF**: 功能全面但性能相对较慢，admin面板对本项目非必需
- **Flask**: 需要更多手工配置，async支持不如FastAPI原生

### Key Advantages

- 自动API文档生成，前端团队协作效率高
- Pydantic数据验证减少错误处理代码
- 异步文件上传处理，不阻塞其他请求
- JSON优先响应，移动端优化效果好

## 决策2: 数据库选择

### Decision: PostgreSQL 15+

### Rationale

PostgreSQL是最适合原神游戏数据特征的数据库选择：

1. **JSON支持优秀**: JSONB数据类型完美存储技能数值、武器效果等半结构化数据
2. **内置全文搜索**: 配合zhparser扩展，支持中文分词和搜索
3. **Python生态成熟**: asyncpg驱动和SQLAlchemy 2.0异步支持
4. **复杂关系查询**: JOIN性能优秀，适合角色→武器→圣遗物推荐链
5. **中文处理**: UTF-8完全支持，包括游戏特殊符号

### Alternatives Considered

- **MongoDB**: 关系查询弱，角色武器推荐需要多次查询或慢速$lookup
- **MySQL**: JSON性能比PostgreSQL的JSONB慢30-50%，全文搜索功能较弱

### Performance Expectations

- 简单查询（按ID）: <10ms
- 复杂关联查询: 50-100ms
- 全文搜索: 100-300ms（可优化至<100ms）
- 100并发用户: 4核服务器CPU使用率<50%

## 数据库架构设计

### Schema设计方法: 关系型（标准化）

主要表结构：
- 核心表: `characters`, `weapons`, `artifacts`, `monsters`, `game_mechanics`, `images`
- 关联表: 多对多关系处理
- JSONB字段: 存储技能数值等灵活数据
- 物化视图: 缓存复杂查询结果

### 搜索策略

**第1阶段（MVP，1-2个月）**:
- PostgreSQL原生全文搜索 + zhparser扩展
- GIN索引优化搜索字段
- 跨实体统一搜索函数
- 目标性能: <200ms搜索响应

**第2阶段（扩展，5-6个月，按需）**:
- 当搜索流量>30%总请求时，集成Elasticsearch
- IK分析器支持中文高级分词
- 拼音搜索、模糊匹配、搜索建议
- 目标性能: <50ms搜索响应

## 技术栈集成

### 核心依赖包

```txt
fastapi==0.104.1          # Web框架
uvicorn[standard]==0.24.0 # ASGI服务器
pydantic==2.5.0           # 数据验证
sqlalchemy==2.0.23        # ORM
asyncpg==0.29.0           # 异步PostgreSQL驱动
python-multipart==0.0.6   # 文件上传支持
pillow==10.1.0            # 图片处理
aiohttp==3.9.1            # 异步HTTP客户端
beautifulsoup4==4.12.2    # HTML解析
redis==5.0.1              # 缓存
celery==5.3.4             # 后台任务
```

### 性能优化策略

1. **数据库索引**: 角色名称、元素、武器类型上建立索引
2. **Redis缓存**: 热点数据1小时缓存，静态数据24小时
3. **CDN图片**: 阿里云OSS或AWS S3，支持WebP格式
4. **连接池**: SQLAlchemy异步引擎，pool_size=20
5. **分页**: 每页限制50条记录，避免大结果集

### 移动端优化

1. **响应大小**: 列表视图（最小）vs 详情视图（完整）分离Schema
2. **图片格式**: 多尺寸支持（缩略图、中等、完整），WebP优先
3. **API版本**: 支持不同客户端版本，`/api/v1/`端点

## 风险评估和缓解

### 技术风险

1. **FastAPI生态相对较新**
   - 缓解: 核心功能稳定，关键集成（SQLAlchemy、Celery、Redis）成熟

2. **团队async Python经验**
   - 缓解: 优秀文档支持，现代Python标准实践，技能提升价值高

3. **数据源不稳定**
   - 缓解: 多数据源冗余，错误处理和重试机制，离线数据备份

### 性能风险

1. **搜索延迟超标**
   - 缓解: 阶段性评估，Elasticsearch集成准备

2. **并发用户超载**
   - 缓解: 水平扩展设计，读写分离，CDN卸载

## Implementation Roadmap

### Phase 1 (MVP - 1-2个月)
1. 搭建FastAPI项目结构
2. PostgreSQL + zhparser部署
3. 核心API端点（角色查询优先）
4. 基础数据同步脚本
5. 性能测试（100并发用户）

### Phase 2 (优化 - 3-4个月)
1. Redis缓存层
2. 图片上传云存储
3. 搜索结果高亮
4. 监控告警（Prometheus + Grafana）
5. 压力测试和查询优化

### Phase 3 (扩展 - 5-6个月，按需)
1. Elasticsearch集成评估
2. 高级搜索功能（拼音、模糊匹配）
3. 数据同步管道优化
4. 多语言支持准备

## 决策确认

所有NEEDS CLARIFICATION项目已解决：

- ✅ **Web框架**: FastAPI（性能、API优先、async支持）
- ✅ **数据库**: PostgreSQL 15+（JSON支持、中文搜索、关系查询）
- ✅ **测试框架**: pytest + pytest-asyncio
- ✅ **部署平台**: Linux服务器 + Docker + nginx反向代理

技术栈选择符合项目章程要求：用户体验优先（<3s加载）、数据准确性（多源同步）、隐私安全（HTTPS、审核）、简化流程（API优化）、规范开发（类型安全、测试覆盖）。