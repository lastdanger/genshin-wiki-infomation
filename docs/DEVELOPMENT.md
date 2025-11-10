# 开发指南 | Development Guide

本文档提供完整的本地开发环境搭建和开发流程指南。

## 📑 目录

- [环境准备](#环境准备)
- [项目设置](#项目设置)
- [开发工作流](#开发工作流)
- [代码规范](#代码规范)
- [调试技巧](#调试技巧)
- [常见问题](#常见问题)

---

## 环境准备

### 必需工具

#### 1. Python 环境

```bash
# 检查 Python 版本（需要 3.8+）
python3 --version

# 安装 pyenv（推荐用于管理 Python 版本）
# macOS
brew install pyenv

# 安装 Python 3.10
pyenv install 3.10.0
pyenv global 3.10.0
```

#### 2. Node.js 环境

```bash
# 检查 Node.js 版本（需要 16+）
node --version
npm --version

# 安装 nvm（推荐用于管理 Node.js 版本）
# macOS/Linux
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash

# 安装 Node.js 18
nvm install 18
nvm use 18
```

#### 3. PostgreSQL

```bash
# macOS
brew install postgresql@14
brew services start postgresql@14

# Ubuntu/Debian
sudo apt-get install postgresql-14

# 验证安装
psql --version
```

#### 4. Redis（可选，用于缓存）

```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server

# 验证安装
redis-cli ping
# 应该返回 PONG
```

---

## 项目设置

### 1. 克隆项目

```bash
git clone https://github.com/lastdanger/genshin-wiki-infomation.git
cd genshin-wiki-infomation
```

### 2. 后端设置

#### 创建数据库

```bash
# 连接到 PostgreSQL
psql -U postgres

# 创建数据库和用户
CREATE DATABASE genshin_wiki;
CREATE USER genshin_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE genshin_wiki TO genshin_user;
\q
```

#### 配置后端环境

```bash
cd backend

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 创建环境配置文件
cp .env.example .env
```

#### 编辑 `.env` 文件

```bash
# 数据库配置
DATABASE_URL=postgresql://genshin_user:your_password@localhost/genshin_wiki

# Redis 配置（可选）
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_ENABLED=true
REDIS_CACHE_TTL=300

# 应用配置
DEBUG=true
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# API 配置
API_V1_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:3002
```

#### 运行数据库迁移

```bash
# 初始化 Alembic（如果还没有）
alembic init alembic

# 创建迁移
alembic revision --autogenerate -m "Initial migration"

# 应用迁移
alembic upgrade head
```

#### 启动后端服务器

```bash
# 开发模式（自动重载）
uvicorn src.main:app --reload --port 8001

# 或使用 make 命令（如果有 Makefile）
make run-backend
```

访问 http://localhost:8001/docs 查看 API 文档。

### 3. 前端设置

```bash
cd frontend

# 安装依赖
npm install

# 创建环境配置文件
cp .env.example .env
```

#### 编辑前端 `.env` 文件

```bash
# API 配置
REACT_APP_API_URL=http://localhost:8001
REACT_APP_API_TIMEOUT=10000

# 应用配置
PORT=3002
REACT_APP_ENV=development

# 功能开关
REACT_APP_ENABLE_CACHE=true
REACT_APP_ENABLE_ANALYTICS=false
```

#### 启动前端服务器

```bash
# 开发模式
npm start

# 或指定端口
PORT=3002 npm start
```

访问 http://localhost:3002 查看应用。

---

## 开发工作流

### Git 工作流

#### 1. 创建功能分支

```bash
# 从 main 分支创建新分支
git checkout main
git pull origin main
git checkout -b feature/your-feature-name
```

#### 2. 开发和提交

```bash
# 查看更改
git status
git diff

# 添加文件
git add .

# 提交（遵循 Conventional Commits）
git commit -m "feat: add user authentication"
git commit -m "fix: correct database connection issue"
git commit -m "docs: update API documentation"
```

#### 3. 推送和创建 PR

```bash
# 推送到远程
git push -u origin feature/your-feature-name

# 在 GitHub 上创建 Pull Request
gh pr create --title "Feature: Your Feature Name" --body "Description of changes"
```

### 代码审查流程

1. **自我审查**：提交前检查代码质量
2. **自动化检查**：CI/CD 运行测试和 lint
3. **同行审查**：至少一位团队成员审查
4. **修改完善**：根据反馈修改代码
5. **合并**：审查通过后合并到 main 分支

---

## 代码规范

### 后端规范（Python）

#### PEP 8 风格指南

```python
# 好的例子
def get_character_by_id(character_id: int) -> Character:
    """获取指定 ID 的角色信息。

    Args:
        character_id: 角色 ID

    Returns:
        Character: 角色对象

    Raises:
        NotFoundError: 角色不存在时抛出
    """
    character = db.query(Character).filter_by(id=character_id).first()
    if not character:
        raise NotFoundError(f"Character with id {character_id} not found")
    return character


# 坏的例子
def getChar(id):  # 命名不规范，缺少类型注解和文档字符串
    c = db.query(Character).filter_by(id=id).first()
    return c
```

#### 代码格式化

```bash
# 使用 Black 格式化代码
black src/

# 使用 isort 整理导入
isort src/

# 使用 flake8 检查代码
flake8 src/

# 使用 mypy 进行类型检查
mypy src/
```

### 前端规范（JavaScript/TypeScript）

#### ESLint 和 Prettier

```bash
# 运行 ESLint 检查
npm run lint

# 自动修复 lint 错误
npm run lint:fix

# 格式化代码
npm run format
```

#### 组件编写规范

```javascript
// 好的例子
/**
 * CharacterCard 组件
 *
 * @param {Object} props - 组件属性
 * @param {Character} props.character - 角色数据
 * @param {Function} props.onClick - 点击回调
 */
const CharacterCard = ({ character, onClick }) => {
  const [isHovered, setIsHovered] = useState(false);

  return (
    <div
      className="character-card"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onClick(character.id)}
    >
      <img src={character.avatar} alt={character.name} />
      <h3>{character.name}</h3>
    </div>
  );
};

// 坏的例子
const CharCard = (props) => {  // 命名不清晰，缺少文档
  return <div onClick={props.clk}>{props.chr.nm}</div>;  // 属性名不明确
};
```

### 提交信息规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

```
<type>(<scope>): <subject>

<body>

<footer>
```

**类型（type）:**
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整（不影响功能）
- `refactor`: 重构
- `test`: 测试相关
- `chore`: 构建/工具链相关
- `perf`: 性能优化

**示例:**

```bash
feat(auth): add JWT authentication

- Implement JWT token generation
- Add login and register endpoints
- Create auth middleware

Closes #123
```

---

## 调试技巧

### 后端调试

#### 1. 使用 print 调试

```python
# 在代码中添加调试输出
print(f"DEBUG: character_id = {character_id}")
print(f"DEBUG: query result = {result}")
```

#### 2. 使用 Python 调试器（pdb）

```python
import pdb

def get_character(character_id):
    pdb.set_trace()  # 设置断点
    character = db.query(Character).filter_by(id=character_id).first()
    return character
```

#### 3. 使用日志

```python
import logging

logger = logging.getLogger(__name__)

def process_data(data):
    logger.info(f"Processing data: {data}")
    try:
        result = complex_operation(data)
        logger.debug(f"Operation result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing data: {e}", exc_info=True)
        raise
```

#### 4. FastAPI 调试

```bash
# 启用详细日志
uvicorn src.main:app --reload --log-level debug

# 使用 VS Code 调试
# launch.json 配置
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.main:app",
        "--reload",
        "--port",
        "8001"
      ],
      "jinja": true
    }
  ]
}
```

### 前端调试

#### 1. 使用 console.log

```javascript
console.log('Character data:', character);
console.table(characters); // 表格形式显示数组
console.error('Error fetching data:', error);
```

#### 2. 使用 React DevTools

```bash
# 安装 React DevTools 浏览器扩展
# Chrome: https://chrome.google.com/webstore/detail/react-developer-tools/
# Firefox: https://addons.mozilla.org/en-US/firefox/addon/react-devtools/
```

#### 3. 使用浏览器调试器

```javascript
// 在代码中设置断点
debugger;

// 或在浏览器开发者工具中设置断点
```

#### 4. 网络请求调试

```javascript
// 在 Axios 拦截器中添加日志
axios.interceptors.request.use(
  config => {
    console.log('Request:', config);
    return config;
  }
);

axios.interceptors.response.use(
  response => {
    console.log('Response:', response);
    return response;
  }
);
```

---

## 常见问题

### 数据库相关

#### Q: 数据库连接失败

```bash
# 检查 PostgreSQL 是否运行
brew services list  # macOS
sudo systemctl status postgresql  # Linux

# 检查连接参数
psql -U genshin_user -d genshin_wiki -h localhost

# 检查 .env 文件中的 DATABASE_URL 配置
```

#### Q: 迁移失败

```bash
# 回滚到上一个版本
alembic downgrade -1

# 查看迁移历史
alembic history

# 重新生成迁移
alembic revision --autogenerate -m "description"
```

### Redis 相关

#### Q: Redis 连接失败

```bash
# 检查 Redis 是否运行
redis-cli ping

# 启动 Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux

# 清空 Redis 缓存
redis-cli FLUSHALL
```

### 前端相关

#### Q: npm install 失败

```bash
# 清理缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json

# 重新安装
npm install
```

#### Q: 端口被占用

```bash
# 查找占用端口的进程
lsof -i :3002  # macOS/Linux
netstat -ano | findstr :3002  # Windows

# 杀死进程
kill -9 <PID>  # macOS/Linux
taskkill /PID <PID> /F  # Windows

# 或使用其他端口
PORT=3003 npm start
```

### 后端相关

#### Q: 依赖安装失败

```bash
# 使用国内镜像
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 升级 pip
pip install --upgrade pip

# 检查 Python 版本
python --version
```

#### Q: 导入模块失败

```bash
# 确保虚拟环境已激活
source venv/bin/activate

# 检查 PYTHONPATH
echo $PYTHONPATH

# 设置 PYTHONPATH（如果需要）
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

---

## 开发工具推荐

### IDE/编辑器

- **VS Code**: 推荐用于前后端开发
  - 扩展：Python, ESLint, Prettier, GitLens
- **PyCharm**: 推荐用于后端开发
- **WebStorm**: 推荐用于前端开发

### 命令行工具

- **httpie**: HTTP 客户端，用于测试 API
  ```bash
  # 安装
  brew install httpie

  # 使用
  http GET localhost:8001/api/characters
  ```

- **jq**: JSON 处理工具
  ```bash
  # 安装
  brew install jq

  # 使用
  curl localhost:8001/api/characters | jq .
  ```

### 数据库工具

- **pgAdmin**: PostgreSQL 图形化管理工具
- **DBeaver**: 通用数据库管理工具
- **Postico**: macOS PostgreSQL 客户端

---

## 性能优化建议

### 后端优化

1. **数据库查询优化**
   - 使用索引
   - 避免 N+1 查询
   - 使用 select_related 和 prefetch_related

2. **缓存策略**
   - 使用 Redis 缓存热点数据
   - 设置合理的 TTL
   - 实现缓存预热

3. **异步处理**
   - 使用 Celery 处理耗时任务
   - 实现异步 API 端点

### 前端优化

1. **代码分割**
   - 使用 React.lazy() 和 Suspense
   - 按路由分割代码

2. **资源优化**
   - 图片懒加载
   - 压缩图片和资源
   - 使用 CDN

3. **渲染优化**
   - 使用 React.memo 避免不必要的重渲染
   - 使用 useMemo 和 useCallback

---

## 测试指南

### 后端测试

```bash
cd backend

# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_characters.py

# 运行并生成覆盖率报告
pytest --cov=src --cov-report=html

# 查看覆盖率报告
open htmlcov/index.html
```

### 前端测试

```bash
cd frontend

# 运行所有测试
npm test

# 运行测试并生成覆盖率
npm test -- --coverage --watchAll=false

# 运行特定测试
npm test -- CharacterCard
```

---

## 获取帮助

- **文档**: 查看 [README.md](../README.md) 和其他文档
- **Issue**: 在 GitHub 上提交 [Issue](https://github.com/lastdanger/genshin-wiki-infomation/issues)
- **讨论**: 参与 [GitHub Discussions](https://github.com/lastdanger/genshin-wiki-infomation/discussions)

---

**祝开发愉快！Happy Coding! 🚀**
