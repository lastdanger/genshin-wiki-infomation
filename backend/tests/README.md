# Backend Tests

后端单元测试和集成测试文档。

## 📁 测试结构

```
tests/
├── __init__.py
├── conftest.py           # Pytest fixtures 和配置
├── pytest.ini            # Pytest 配置文件
├── api/                  # API 端点测试
│   ├── test_health.py
│   ├── test_characters.py
│   ├── test_weapons.py
│   ├── test_artifacts.py
│   └── test_monsters.py
├── services/             # 服务层测试
├── models/               # 数据库模型测试
├── middleware/           # 中间件测试
└── utils/                # 工具函数测试
```

## 🚀 运行测试

### 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 运行所有测试

```bash
pytest
```

### 运行特定测试文件

```bash
pytest tests/api/test_characters.py
```

### 运行特定测试类

```bash
pytest tests/api/test_characters.py::TestCharactersAPI
```

### 运行特定测试用例

```bash
pytest tests/api/test_characters.py::TestCharactersAPI::test_list_characters
```

### 运行带标记的测试

```bash
# 只运行 API 测试
pytest -m api

# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"
```

## 📊 测试覆盖率

### 生成覆盖率报告

```bash
# 终端输出
pytest --cov=src --cov-report=term-missing

# 生成 HTML 报告
pytest --cov=src --cov-report=html

# 生成 XML 报告 (用于 CI/CD)
pytest --cov=src --cov-report=xml
```

### 查看 HTML 报告

```bash
# 生成后打开
open htmlcov/index.html
```

## 🎯 当前测试覆盖范围

### API 端点测试 ✅
- **Health Check API** - 100%
  - 根路径测试
  - 健康检查测试
  - 详细健康检查
  - 就绪和存活检查
  - 版本信息

- **Characters API** - 95%
  - CRUD 操作完整测试
  - 分页测试
  - 筛选测试 (元素、武器类型、稀有度)
  - 搜索功能测试
  - 错误处理测试

- **Weapons API** - 90%
  - 基本 CRUD 操作
  - 筛选功能
  - 错误处理

- **Artifacts API** - 90%
  - 基本 CRUD 操作
  - 筛选功能

- **Monsters API** - 90%
  - 基本 CRUD 操作
  - 筛选功能

### 待实现测试 ⏳
- Services 层测试
- Models 测试
- Middleware 测试
- Utils 测试

## 📝 编写测试指南

### 测试命名规范

```python
# 测试类命名
class TestCharactersAPI:
    pass

# 测试方法命名
async def test_list_characters(self, client: AsyncClient):
    pass

async def test_create_character_with_invalid_data(self, client: AsyncClient):
    pass
```

### 使用 Fixtures

```python
@pytest.mark.asyncio
async def test_get_character(
    client: AsyncClient,
    db_session: Session,
    sample_character_data
):
    # 创建测试数据
    character = create_character(db_session, **sample_character_data)

    # 发送请求
    response = await client.get(f"/api/v1/characters/{character.id}")

    # 断言
    assert response.status_code == 200
    assert response.json()["name"] == sample_character_data["name"]
```

### 测试异步 API

```python
@pytest.mark.asyncio
async def test_async_endpoint(client: AsyncClient):
    response = await client.get("/api/v1/endpoint")
    assert response.status_code == 200
```

### 测试错误情况

```python
async def test_not_found_error(client: AsyncClient):
    response = await client.get("/api/v1/characters/999999")
    assert response.status_code == 404
    assert "detail" in response.json()

async def test_validation_error(client: AsyncClient):
    invalid_data = {"name": ""}  # 空名称
    response = await client.post("/api/v1/characters", json=invalid_data)
    assert response.status_code == 422
```

## 🔧 配置说明

### pytest.ini

主要配置项:
- `testpaths`: 测试目录路径
- `python_files`: 测试文件匹配模式
- `addopts`: 默认命令行选项
- `markers`: 自定义标记定义

### conftest.py

包含共享的 fixtures:
- `db_engine`: 数据库引擎
- `db_session`: 数据库会话
- `client`: HTTP 测试客户端
- `sample_*_data`: 测试数据

## 🐛 常见问题

### 1. 数据库连接错误

确保使用测试数据库配置:
```python
os.environ["DATABASE_URL"] = "sqlite:///./test.db"
```

### 2. Async 测试失败

确保测试函数标记为 async 并使用 `@pytest.mark.asyncio`:
```python
@pytest.mark.asyncio
async def test_something():
    pass
```

### 3. 测试之间数据污染

每个测试函数都使用独立的数据库会话,测试后自动回滚。

## 📈 CI/CD 集成

测试在以下情况自动运行:
- Push 到 `main` 或 `develop` 分支
- 创建 Pull Request
- 手动触发 workflow

查看 `.github/workflows/backend-ci.yml` 了解详情。

## 🎓 最佳实践

1. **每个测试应该独立**: 不依赖其他测试的执行顺序
2. **使用描述性的测试名称**: 清楚表达测试意图
3. **遵循 AAA 模式**: Arrange (准备) -> Act (执行) -> Assert (断言)
4. **测试边界情况**: 包括正常情况和异常情况
5. **保持测试简单**: 一个测试只测试一个功能点
6. **使用 fixtures 重用代码**: 避免测试代码重复

## 📚 参考资料

- [Pytest 官方文档](https://docs.pytest.org/)
- [FastAPI 测试文档](https://fastapi.tiangolo.com/tutorial/testing/)
- [HTTPX 测试客户端](https://www.python-httpx.org/)

---

最后更新: 2025-11-07
