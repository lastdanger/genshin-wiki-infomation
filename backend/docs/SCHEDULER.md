# 定时任务调度系统

## 概述

本项目使用 APScheduler 实现了完整的定时爬取任务调度系统，支持自动化数据更新。

## 功能特性

- 🕐 **Cron 表达式调度** - 支持标准 cron 表达式，灵活配置执行时间
- ⏱️ **间隔调度** - 支持按固定间隔执行任务（小时为单位）
- 📊 **执行历史** - 自动记录任务执行历史，包括成功/失败状态和耗时
- 🔧 **任务管理** - 支持创建、删除、暂停、恢复任务
- 🚀 **手动触发** - 可以立即执行任务而不影响定时计划
- 🔄 **自动启动** - 调度器随应用启动自动运行

## 默认任务

系统默认配置了两个定时任务：

1. **武器数据爬取** (`weapons_weekly`)
   - 执行时间：每周日凌晨 2:00
   - Cron: `0 2 * * 0`
   - 任务内容：爬取所有武器数据并更新数据库

2. **圣遗物数据爬取** (`artifacts_weekly`)
   - 执行时间：每周日凌晨 3:00
   - Cron: `0 3 * * 0`
   - 任务内容：爬取所有圣遗物套装数据并更新数据库

## API 端点

### 1. 获取调度器状态

```bash
GET /api/scheduler/status
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "running": true,
    "status": "running"
  },
  "message": "调度器运行中"
}
```

### 2. 设置默认任务

```bash
POST /api/scheduler/setup/default
```

快速设置武器和圣遗物的每周定时任务（每周日执行）。

**响应示例：**
```json
{
  "success": true,
  "data": {
    "jobs": [
      {
        "id": "weapons_weekly",
        "name": "武器数据定时爬取",
        "next_run_time": "2025-11-17T02:00:00+08:00",
        "trigger": "cron[month='*', day='*', day_of_week='0', hour='2', minute='0']",
        "pending": false
      },
      {
        "id": "artifacts_weekly",
        "name": "圣遗物数据定时爬取",
        "next_run_time": "2025-11-17T03:00:00+08:00",
        "trigger": "cron[month='*', day='*', day_of_week='0', hour='3', minute='0']",
        "pending": false
      }
    ],
    "total": 2
  },
  "message": "成功设置默认定时任务"
}
```

### 3. 获取所有任务

```bash
GET /api/scheduler/jobs
```

### 4. 创建新任务

#### 使用 Cron 表达式

```bash
POST /api/scheduler/jobs
Content-Type: application/json

{
  "job_type": "weapons",
  "schedule_type": "cron",
  "cron": "0 */6 * * *",
  "job_id": "weapons_6h"
}
```

#### 使用间隔调度

```bash
POST /api/scheduler/jobs
Content-Type: application/json

{
  "job_type": "artifacts",
  "schedule_type": "interval",
  "interval_hours": 12,
  "job_id": "artifacts_12h"
}
```

**任务类型 (job_type):**
- `weapons` - 武器数据爬取
- `artifacts` - 圣遗物数据爬取
- `all` - 完整爬取（武器 + 圣遗物）

### 5. 手动触发任务

```bash
POST /api/scheduler/jobs/trigger
Content-Type: application/json

{
  "job_type": "weapons"
}
```

立即执行一次爬取任务，不影响定时任务的执行计划。

### 6. 暂停任务

```bash
POST /api/scheduler/jobs/{job_id}/pause
```

### 7. 恢复任务

```bash
POST /api/scheduler/jobs/{job_id}/resume
```

### 8. 删除任务

```bash
DELETE /api/scheduler/jobs/{job_id}
```

### 9. 查看执行历史

```bash
GET /api/scheduler/history?limit=20
```

**响应示例：**
```json
{
  "success": true,
  "data": {
    "history": [
      {
        "job_id": "scrape_weapons",
        "job_name": "武器数据爬取",
        "start_time": "2025-11-12T02:00:00",
        "end_time": "2025-11-12T02:05:32",
        "elapsed_seconds": 332.5,
        "status": "success",
        "stats": {
          "scraped_count": 158,
          "created": 5,
          "updated": 153,
          "skipped": 0,
          "errors": 0
        }
      }
    ],
    "total": 1
  },
  "message": "成功获取1条历史记录"
}
```

## Cron 表达式示例

```
# 每天凌晨2点
0 2 * * *

# 每6小时执行一次
0 */6 * * *

# 每周日凌晨3点
0 3 * * 0

# 每月1号凌晨4点
0 4 1 * *

# 工作日早上9点
0 9 * * 1-5
```

## 任务执行流程

1. **任务触发** - 根据 cron 表达式或间隔时间自动触发
2. **数据爬取** - 调用相应的爬虫服务获取数据
3. **数据存储** - 自动更新数据库（创建新数据或更新现有数据）
4. **记录历史** - 保存执行结果、耗时、统计信息
5. **错误处理** - 失败时记录错误信息，不影响后续任务

## 配置说明

### 任务并发控制

每个任务的 `max_instances=1`，确保同一时间只有一个实例运行，避免数据竞争。

### 历史记录限制

默认保留最近 100 条执行历史记录，超出部分自动删除。

### 任务重试

单个爬虫请求失败时会自动重试（最多3次），但整个任务失败不会自动重试，需要等待下次计划执行或手动触发。

## 使用示例

### 场景1：设置默认定时任务

```bash
# 首次启动或需要重置默认任务时
curl -X POST http://localhost:8001/api/scheduler/setup/default
```

### 场景2：创建自定义任务

```bash
# 每4小时更新一次武器数据
curl -X POST http://localhost:8001/api/scheduler/jobs \
  -H "Content-Type: application/json" \
  -d '{
    "job_type": "weapons",
    "schedule_type": "interval",
    "interval_hours": 4,
    "job_id": "weapons_4h"
  }'
```

### 场景3：手动触发数据更新

```bash
# 需要立即更新数据时
curl -X POST http://localhost:8001/api/scheduler/jobs/trigger \
  -H "Content-Type: application/json" \
  -d '{"job_type": "all"}'
```

### 场景4：查看任务执行情况

```bash
# 查看最近的任务执行记录
curl http://localhost:8001/api/scheduler/history?limit=10
```

## 监控建议

1. **定期检查执行历史** - 确保任务正常执行
2. **关注失败记录** - 及时处理错误情况
3. **监控执行耗时** - 异常耗时可能表示网络问题
4. **验证数据更新** - 定期确认数据库数据是最新的

## 故障排查

### 任务没有执行

1. 检查调度器状态：`GET /api/scheduler/status`
2. 确认任务是否存在：`GET /api/scheduler/jobs`
3. 查看任务是否被暂停
4. 检查服务器时区设置

### 任务执行失败

1. 查看执行历史获取错误信息：`GET /api/scheduler/history`
2. 检查网络连接是否正常
3. 确认目标网站是否可访问
4. 查看服务器日志获取详细错误

### 数据没有更新

1. 确认任务成功执行（status: "success"）
2. 检查 stats 中的 created/updated 数量
3. 查看数据库连接是否正常
4. 手动触发任务进行测试

## 注意事项

1. **时区** - 所有时间使用服务器本地时区（默认为 Asia/Shanghai）
2. **资源** - 爬取任务会占用网络和CPU资源，避免设置过于频繁的任务
3. **限流** - 爬虫内置了请求限流机制，尊重目标网站的 robots.txt
4. **备份** - 建议在重要数据更新前先备份数据库

## 开发者指南

### 添加新的任务类型

在 `src/services/scheduler_service.py` 中添加新的任务函数：

```python
async def _scrape_new_data_job(self):
    """新数据爬取任务"""
    job_id = "scrape_new_data"
    start_time = datetime.now()

    try:
        # 执行爬取逻辑
        scraper = NewDataScraper()
        data = await scraper.scrape()

        # 存储数据
        stats = await storage_service.store_new_data(data)

        # 记录历史
        self._add_history({...})

    except Exception as e:
        # 错误处理
        self._add_history({...})
```

然后在 API 路由中添加对应的处理逻辑。

### 修改默认任务配置

编辑 `src/api/scheduler.py` 中的 `setup_default_jobs` 函数：

```python
scheduler_service.add_weapons_job(cron="0 2 * * *", job_id="weapons_daily")
```

修改 cron 表达式即可调整执行时间。
