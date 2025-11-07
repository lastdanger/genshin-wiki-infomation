# 原神游戏信息网站

一个展示原神游戏相关信息的全栈 Web 应用，包括角色、武器、圣遗物、怪物等详细信息。

## 🚀 快速开始

### 端口配置

- **后端 API**: http://localhost:8001
- **前端应用**: http://localhost:3002
- **API 文档**: http://localhost:8001/docs

详细端口配置请查看 [PORT_CONFIG.md](./PORT_CONFIG.md)

### 前置要求

- Python 3.8+
- Node.js 16+
- PostgreSQL 12+

### 安装步骤

#### 1. 克隆项目

```bash
git clone <repository-url>
cd genshin_wiki_information
```

#### 2. 启动后端 (端口 8001)

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或 venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动服务器
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

#### 3. 启动前端 (端口 3002)

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
PORT=3002 npm start
# 或者直接 npm start (已在 .env 中配置)
```

#### 4. 访问应用

- 前端: http://localhost:3002
- 后端 API 文档: http://localhost:8001/docs

## 📁 项目结构

```
genshin_wiki_information/
├── backend/                 # FastAPI 后端
│   ├── src/
│   │   ├── main.py         # 应用入口
│   │   ├── config.py       # 配置文件
│   │   ├── models/         # 数据库模型
│   │   ├── routes/         # API 路由
│   │   └── services/       # 业务逻辑
│   └── requirements.txt    # Python 依赖
│
├── frontend/               # React 前端
│   ├── src/
│   │   ├── components/    # React 组件
│   │   │   └── ErrorBoundary/  # 错误边界组件
│   │   ├── pages/         # 页面组件
│   │   ├── services/      # API 服务层
│   │   │   ├── base/      # 基础服务
│   │   │   └── errors/    # 错误处理
│   │   └── App.jsx        # 应用入口
│   ├── package.json       # Node 依赖
│   └── .env               # 环境配置
│
├── specs/                 # Speckit 规格文档
│   └── 001-genshin-info-website/
│       ├── spec.md        # 功能规格
│       ├── plan.md        # 实施计划
│       ├── tasks.md       # 任务列表
│       └── ARCHITECTURE_IMPROVEMENT.md
│
└── PORT_CONFIG.md         # 端口配置文档
```

## 🏗️ 技术栈

### 后端
- **框架**: FastAPI
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **服务器**: Uvicorn

### 前端
- **框架**: React 18
- **路由**: React Router v6
- **HTTP 客户端**: Axios
- **状态管理**: React Hooks
- **样式**: CSS Modules

## 📖 核心功能

### 1. 角色系统
- 角色列表和详情页
- 按元素、武器类型、稀有度筛选
- 角色技能和天赋展示

### 2. 武器系统
- 武器图鉴
- 武器对比功能
- 根据角色推荐武器

### 3. 圣遗物系统
- 圣遗物套装列表
- 主属性和副属性详情
- 角色圣遗物推荐

### 4. 怪物系统
- 怪物图鉴
- 怪物属性和抗性
- 掉落物品信息

### 5. 全局搜索
- 跨实体搜索（角色、武器、圣遗物、怪物）
- 搜索历史记录
- 搜索建议

## 🎯 架构亮点

### API 服务层
- **BaseAPIService**: 统一的 HTTP 请求封装
- **错误分类**: NetworkError, BusinessError, SystemError
- **自动重试**: 指数退避算法
- **请求拦截**: 自动添加认证和日志

### 错误处理
- **GlobalErrorBoundary**: 全局错误捕获
- **ErrorBoundary**: 可配置的局部错误边界
- **ErrorMessage**: 用户友好的错误提示
- **RetryButton**: 支持重试和倒计时

详细架构设计请查看 [specs/001-genshin-info-website/ARCHITECTURE_IMPROVEMENT.md](./specs/001-genshin-info-website/ARCHITECTURE_IMPROVEMENT.md)

## 🔧 开发

### 前端开发

```bash
cd frontend

# 启动开发服务器
npm start

# 构建生产版本
npm run build

# 运行测试
npm test
```

### 后端开发

```bash
cd backend

# 启动开发服务器（自动重载）
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# 运行测试
pytest

# 查看 API 文档
# 访问 http://localhost:8001/docs
```

## 📝 API 文档

后端使用 FastAPI 自动生成 API 文档：
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🚧 当前状态

### 已完成 ✅
- [x] 基础架构搭建
- [x] API 服务层重构
- [x] 错误处理机制
- [x] 错误边界组件
- [x] 全局搜索功能
- [x] 前端构建成功

### 进行中 🔄
- [ ] 后端 API 端点实现
- [ ] 数据库数据导入
- [ ] 集成测试

### 待开始 ⏸️
- [ ] 性能优化
- [ ] 日志和监控
- [ ] 部署配置

## 📚 相关文档

- [功能规格 (spec.md)](./specs/001-genshin-info-website/spec.md)
- [实施计划 (plan.md)](./specs/001-genshin-info-website/plan.md)
- [任务列表 (tasks.md)](./specs/001-genshin-info-website/tasks.md)
- [架构改进总结](./specs/001-genshin-info-website/ARCHITECTURE_IMPROVEMENT.md)
- [API 服务使用文档](./frontend/src/services/README.md)
- [端口配置](./PORT_CONFIG.md)

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

---

**最后更新**: 2025-11-06
