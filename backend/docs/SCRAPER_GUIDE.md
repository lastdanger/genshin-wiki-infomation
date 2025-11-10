# 爬虫使用指南 | Scraper Guide

原神游戏信息爬虫系统，用于从多个数据源自动爬取和更新角色、武器、圣遗物等数据。

## 📑 目录

- [功能特性](#功能特性)
- [数据源](#数据源)
- [架构设计](#架构设计)
- [使用方法](#使用方法)
- [API 端点](#api-端点)
- [配置选项](#配置选项)
- [最佳实践](#最佳实践)

---

## 功能特性

### ✨ 核心功能

- **多数据源支持**：支持从 Bilibili Game Wiki、HomdGCat Wiki 等多个来源爬取数据
- **异步爬取**：使用 `aiohttp` 异步 HTTP 请求，高效并发爬取
- **智能速率限制**：自动限制请求频率，避免对目标网站造成压力
- **请求重试机制**：指数退避算法，自动重试失败的请求
- **增量更新**：只更新有变化的数据，避免重复写入
- **User-Agent 轮换**：随机轮换 User-Agent，模拟真实浏览器
- **错误处理**：完善的错误捕获和日志记录

### 📊 数据类型

目前支持爬取：
- ✅ **角色数据**：基础信息、属性、技能、天赋、命之座、突破材料
- 🔄 **武器数据**：基础属性、副词条、特效、适配角色（TODO）
- 🔄 **圣遗物数据**：套装效果、词条推荐（TODO）

---

## 数据源

### 1. Bilibili Game Wiki

- **URL**: https://wiki.biligame.com/ys/
- **特点**：中文数据、更新及时、内容详细
- **爬取内容**：角色列表、角色详情、技能信息

### 2. HomdGCat Wiki

- **URL**: https://homdgcat.wiki/gi/char
- **特点**：数据结构清晰、API 友好
- **爬取内容**：角色统计数据、装备推荐

### ⚠️ 注意事项

- **遵守 robots.txt**：爬虫会检查并遵守网站的 robots.txt 规则
- **合理速率**：默认 1 请求/秒，避免对目标网站造成压力
- **友好 User-Agent**：使用明确标识的 User-Agent
- **仅用于学习**：本爬虫仅用于个人学习和非商业用途

---

## 架构设计

### 模块结构

```
backend/src/scrapers/
├── __init__.py              # 模块入口
├── base_scraper.py          # 基础爬虫类
├── character_scraper.py     # 角色数据爬虫
├── data_storage.py          # 数据存储服务
└── weapon_scraper.py        # 武器数据爬虫（TODO）
```

### 类图

```
┌─────────────────────┐
│   BaseScraper       │
│  (抽象基类)          │
├─────────────────────┤
│ + config            │
│ + session           │
│ + fetch()           │
│ + parse_html()      │
│ + scrape() abstract │
└─────────────────────┘
          ▲
          │ 继承
          │
┌─────────┴───────────┐
│ CharacterScraper    │
├─────────────────────┤
│ + scrape()          │
│ + scrape_list()     │
│ + scrape_details()  │
└─────────────────────┘
```

### 工作流程

```
1. 初始化爬虫
   ├── 创建 HTTP Session
   ├── 加载配置
   └── 设置速率限制

2. 爬取数据
   ├── 获取角色列表
   │   ├── 发送 HTTP 请求
   │   ├── 解析 HTML
   │   └── 提取基础信息
   │
   └── 遍历角色详情
       ├── 获取详情页
       ├── 解析详细信息
       └── 合并数据

3. 存储数据
   ├── 检查数据是否存在
   ├── 比较是否有变化
   └── 增量更新或创建
```

---

## 使用方法

### 1. 通过 API 手动触发

#### 触发角色数据爬取

```bash
curl -X POST http://localhost:8001/api/scraper/characters/trigger
```

#### 查看爬取状态

```bash
curl http://localhost:8001/api/scraper/status
```

#### 查看爬取统计

```bash
curl http://localhost:8001/api/scraper/stats
```

### 2. 在代码中使用

```python
from src.scrapers.character_scraper import CharacterScraper
from src.scrapers.base_scraper import ScraperConfig
from src.scrapers.data_storage import DataStorageService
from src.db.session import get_db

# 配置爬虫
config = ScraperConfig(
    requests_per_second=1.0,  # 每秒1个请求
    max_retries=3,            # 最多重试3次
    timeout_seconds=30,       # 超时30秒
)

# 创建爬虫实例
scraper = CharacterScraper(config)

# 执行爬取
async with scraper:
    # 爬取所有角色数据
    characters = await scraper.scrape()

    # 存储到数据库
    async with get_db() as db:
        storage = DataStorageService(db)
        stats = await storage.store_characters(characters)
        print(f"Created: {stats['created']}, Updated: {stats['updated']}")
```

### 3. 定时任务（Celery）

```python
# TODO: 配置 Celery 定时任务
from celery import Celery
from celery.schedules import crontab

app = Celery('tasks')

@app.task
def scrape_characters():
    """每天凌晨3点爬取角色数据"""
    # 爬取逻辑
    pass

app.conf.beat_schedule = {
    'scrape-characters-daily': {
        'task': 'tasks.scrape_characters',
        'schedule': crontab(hour=3, minute=0),  # 每天凌晨3点
    },
}
```

---

## API 端点

### POST /api/scraper/characters/trigger

手动触发角色数据爬取。

**请求示例：**
```bash
curl -X POST http://localhost:8001/api/scraper/characters/trigger
```

**响应示例：**
```json
{
  "success": true,
  "message": "Character scraping task started in background",
  "status": "started"
}
```

### GET /api/scraper/status

获取爬虫当前状态。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "is_running": false,
    "current_task": null,
    "last_run": "2025-11-10T10:30:00",
    "last_result": {
      "success": true,
      "scraper_stats": {
        "requests": 50,
        "errors": 2,
        "success_rate": 96.0
      },
      "storage_stats": {
        "created": 10,
        "updated": 35,
        "skipped": 3,
        "errors": 2
      },
      "total_characters": 48
    }
  }
}
```

### GET /api/scraper/stats

获取爬虫统计信息。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "last_run": "2025-11-10T10:30:00",
    "is_running": false,
    "last_result": {
      "success": true,
      "total_characters": 48
    }
  }
}
```

### GET /api/scraper/config

获取爬虫配置。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "requests_per_second": 1.0,
    "max_retries": 3,
    "timeout_seconds": 30,
    "respect_robots_txt": true
  }
}
```

---

## 配置选项

### ScraperConfig 参数

```python
@dataclass
class ScraperConfig:
    # 速率限制
    requests_per_second: float = 1.0       # 每秒请求数
    min_delay_seconds: float = 1.0         # 最小延迟（秒）
    max_delay_seconds: float = 3.0         # 最大延迟（秒）

    # 重试配置
    max_retries: int = 3                   # 最大重试次数
    retry_delay_seconds: float = 2.0       # 重试延迟（秒）
    retry_backoff_factor: float = 2.0      # 指数退避因子

    # 请求超时
    timeout_seconds: int = 30              # 超时时间（秒）

    # 连接池
    max_connections: int = 10              # 最大连接数
    max_connections_per_host: int = 5      # 每个主机最大连接数

    # User-Agent 列表
    user_agents: List[str] = [...]         # User-Agent 列表

    # 代理配置（可选）
    proxy_url: Optional[str] = None        # 代理 URL

    # Robots.txt
    respect_robots_txt: bool = True        # 是否遵守 robots.txt
```

### 环境变量

可以通过环境变量配置某些参数：

```bash
# .env 文件
SCRAPER_REQUESTS_PER_SECOND=0.5
SCRAPER_MAX_RETRIES=5
SCRAPER_TIMEOUT=60
SCRAPER_PROXY_URL=http://proxy.example.com:8080
```

---

## 最佳实践

### 1. 速率限制

```python
# 推荐配置：保守的速率限制
config = ScraperConfig(
    requests_per_second=0.5,  # 2秒1个请求
    min_delay_seconds=2.0,
    max_delay_seconds=5.0,
)
```

### 2. 错误处理

```python
try:
    async with scraper:
        characters = await scraper.scrape()
except Exception as e:
    logger.error(f"Scraping failed: {e}")
    # 发送告警通知
    send_alert(f"Scraper error: {e}")
```

### 3. 增量更新

```python
# DataStorageService 会自动检测数据变化
# 只更新有变化的记录，跳过相同数据
storage = DataStorageService(db)
stats = await storage.store_characters(characters)

# 查看更新统计
print(f"Created: {stats['created']}")   # 新创建
print(f"Updated: {stats['updated']}")   # 更新
print(f"Skipped: {stats['skipped']}")   # 跳过（无变化）
```

### 4. 监控和日志

```python
import logging

# 配置详细日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 爬虫会自动记录：
# - 请求 URL 和状态
# - 重试次数和原因
# - 解析错误
# - 存储统计
```

### 5. 定期清理

```python
# 定期清理过期数据
async def cleanup_old_data(db: AsyncSession):
    # 删除3个月未更新的数据
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    await db.execute(
        delete(Character).where(Character.updated_at < cutoff_date)
    )
    await db.commit()
```

---

## 故障排查

### 问题 1：爬取失败

**症状**：HTTP 请求失败，返回 403 或 429 错误

**解决方案**：
```python
# 1. 降低请求频率
config.requests_per_second = 0.3  # 更保守的速率

# 2. 增加重试次数
config.max_retries = 5

# 3. 使用代理
config.proxy_url = "http://your-proxy.com:8080"
```

### 问题 2：解析失败

**症状**：无法提取数据，返回 None

**解决方案**：
```python
# 检查网站结构是否变化
html = await scraper.fetch(url)
soup = scraper.parse_html(html)

# 打印 HTML 结构
print(soup.prettify())

# 调整选择器
# 从 .character-card 改为 .role-box
```

### 问题 3：数据库写入失败

**症状**：爬取成功但存储失败

**解决方案**：
```python
# 检查数据完整性
for char in characters:
    if not char.get("name"):
        logger.warning(f"Missing name: {char}")
    if not char.get("element"):
        logger.warning(f"Missing element for {char.get('name')}")

# 检查数据库连接
await db.execute("SELECT 1")
```

---

## 开发计划

### 已完成 ✅

- [x] 基础爬虫框架
- [x] 角色数据爬虫
- [x] 增量数据存储
- [x] API 端点
- [x] 速率限制和重试

### 进行中 🔄

- [ ] 武器数据爬虫
- [ ] 圣遗物数据爬虫
- [ ] Celery 定时任务

### 计划中 📝

- [ ] 数据验证和清洗
- [ ] 爬虫监控仪表盘
- [ ] 多线程爬取优化
- [ ] 数据对比和变更追踪
- [ ] 自动化测试

---

## 许可证

MIT License

---

**最后更新**: 2025-11-10
