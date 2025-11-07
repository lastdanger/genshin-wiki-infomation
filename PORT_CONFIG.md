# 端口配置文档

## 项目端口使用规范

**更新日期**: 2025-11-06

### 统一端口配置

| 服务 | 端口 | 协议 | 说明 |
|------|------|------|------|
| **后端 API 服务器** | `8001` | HTTP | FastAPI + Uvicorn |
| **前端开发服务器** | `3002` | HTTP | React Dev Server (npm start) |
| **数据库** | `5432` | TCP | PostgreSQL (默认) |

### 访问地址

- **前端访问**: http://localhost:3002
- **后端 API**: http://localhost:8001
- **API 文档**: http://localhost:8001/docs (Swagger UI)
- **数据库连接**: postgresql://localhost:5432

### 配置文件位置

#### 后端配置
- **启动命令**: `python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload`
- **配置文件**: `backend/src/config.py`

#### 前端配置
- **启动命令**: `PORT=3002 npm start`
- **代理配置**: `frontend/package.json` 中的 `"proxy": "http://localhost:8001"`
- **环境变量**: `frontend/.env`
  ```
  PORT=3002
  REACT_APP_API_BASE_URL=http://localhost:8001/api
  ```

### 注意事项

1. **前端代理**: 在开发模式下，前端通过 `package.json` 的 `proxy` 配置将 `/api/*` 请求代理到后端
2. **CORS 配置**: 后端已配置 CORS 允许来自 `http://localhost:3002` 的请求
3. **生产环境**: 生产环境需要配置 Nginx 反向代理或使用环境变量覆盖端口

### 启动顺序

1. **启动数据库** (如果使用 Docker)
   ```bash
   docker-compose up -d postgres
   ```

2. **启动后端服务器** (端口 8001)
   ```bash
   cd backend
   python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
   ```

3. **启动前端开发服务器** (端口 3002)
   ```bash
   cd frontend
   PORT=3002 npm start
   ```

### 端口冲突处理

如果端口被占用，可以使用以下命令检查和清理：

```bash
# 查看占用端口的进程
lsof -i :8001
lsof -i :3002

# 杀死占用端口的进程
kill -9 <PID>
```

### 历史记录

- **2025-11-06**: 统一配置 - 后端 8001，前端 3002
- 之前使用: 后端 8000/8001/8002 (不统一), 前端 3000 (默认)

### 相关文件

- `backend/src/main.py` - 后端主入口
- `backend/src/config.py` - 后端配置
- `frontend/package.json` - 前端配置和代理
- `frontend/.env` - 前端环境变量
- `frontend/src/services/base/BaseAPIService.js` - API 基础服务配置
