# 进程管理和项目启动指南

**更新日期**: 2025-11-06

## 📋 快速命令参考

### 查看当前运行的进程

```bash
# 查看所有 Python 服务器进程
ps aux | grep -E "python.*uvicorn|python.*main.py" | grep -v grep

# 查看所有 Node.js 开发服务器进程
ps aux | grep -E "node.*react-scripts|npm.*start" | grep -v grep

# 查看端口占用情况
lsof -i :8001  # 后端端口
lsof -i :3002  # 前端端口
lsof -i :5432  # 数据库端口
```

### 关闭进程

#### 方法 1: 通过端口号杀死进程

```bash
# 杀死占用 8001 端口的进程（后端）
lsof -ti :8001 | xargs kill -9

# 杀死占用 3002 端口的进程（前端）
lsof -ti :3002 | xargs kill -9

# 一键清理所有项目相关端口
lsof -ti :8001 | xargs kill -9 && lsof -ti :3002 | xargs kill -9
```

#### 方法 2: 通过进程 ID (PID) 杀死

```bash
# 1. 找到进程 PID
lsof -i :8001
# 输出示例:
# COMMAND   PID  USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
# Python  12345 user    4u  IPv4 ...      0t0  TCP *:8001 (LISTEN)

# 2. 使用 PID 杀死进程
kill -9 12345

# 或者一行命令搞定
kill -9 $(lsof -ti :8001)
```

#### 方法 3: 通过进程名称杀死

```bash
# 杀死所有 uvicorn 进程
pkill -9 -f uvicorn

# 杀死所有 react-scripts 进程
pkill -9 -f react-scripts

# 杀死所有与项目相关的进程
pkill -9 -f "genshin_wiki"
```

### 一键清理脚本

创建一个清理脚本 `cleanup.sh`:

```bash
#!/bin/bash
# cleanup.sh - 清理所有项目相关进程

echo "🧹 清理项目进程..."

# 杀死后端进程 (8001, 8002)
echo "停止后端服务器..."
lsof -ti :8001 | xargs kill -9 2>/dev/null
lsof -ti :8002 | xargs kill -9 2>/dev/null
pkill -9 -f "uvicorn.*genshin" 2>/dev/null

# 杀死前端进程 (3002, 3000)
echo "停止前端服务器..."
lsof -ti :3002 | xargs kill -9 2>/dev/null
lsof -ti :3000 | xargs kill -9 2>/dev/null
pkill -9 -f "react-scripts" 2>/dev/null

echo "✅ 清理完成！"

# 验证
echo ""
echo "检查剩余进程:"
lsof -i :8001 2>/dev/null || echo "  ✓ 端口 8001 已释放"
lsof -i :3002 2>/dev/null || echo "  ✓ 端口 3002 已释放"
```

**使用方法**:
```bash
chmod +x cleanup.sh
./cleanup.sh
```

---

## 🚀 完整启动流程

### 方法 1: 分步启动（推荐用于开发）

#### 步骤 1: 清理旧进程

```bash
# 清理所有旧进程
./cleanup.sh

# 或手动清理
lsof -ti :8001 | xargs kill -9
lsof -ti :3002 | xargs kill -9
```

#### 步骤 2: 启动后端 (端口 8001)

```bash
# 打开新终端窗口 1
cd "/Users/anker/Desktop/learn project/Speckit/genshin_wiki_information/backend"

# 激活虚拟环境（如果有）
# source venv/bin/activate

# 启动后端服务器
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload
```

**验证后端启动成功**:
```bash
# 在另一个终端运行
curl http://localhost:8001/docs
# 或在浏览器访问: http://localhost:8001/docs
```

#### 步骤 3: 启动前端 (端口 3002)

```bash
# 打开新终端窗口 2
cd "/Users/anker/Desktop/learn project/Speckit/genshin_wiki_information/frontend"

# 安装依赖（首次运行）
# npm install

# 启动前端开发服务器
npm start
# 会自动使用 .env 中配置的 PORT=3002
```

**验证前端启动成功**:
- 浏览器自动打开 http://localhost:3002
- 或手动访问: http://localhost:3002

---

### 方法 2: 一键启动脚本

创建启动脚本 `start-all.sh`:

```bash
#!/bin/bash
# start-all.sh - 一键启动所有服务

PROJECT_ROOT="/Users/anker/Desktop/learn project/Speckit/genshin_wiki_information"

echo "🚀 启动原神信息网站项目..."
echo ""

# 1. 清理旧进程
echo "1️⃣ 清理旧进程..."
lsof -ti :8001 | xargs kill -9 2>/dev/null
lsof -ti :3002 | xargs kill -9 2>/dev/null
sleep 1
echo "   ✓ 清理完成"
echo ""

# 2. 启动后端
echo "2️⃣ 启动后端服务器 (端口 8001)..."
cd "$PROJECT_ROOT/backend"

# 后台启动后端
nohup python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload \
  > ../logs/backend.log 2>&1 &
BACKEND_PID=$!

echo "   后端 PID: $BACKEND_PID"
echo "   等待后端启动..."
sleep 3

# 检查后端是否启动成功
if lsof -i :8001 > /dev/null 2>&1; then
  echo "   ✓ 后端启动成功: http://localhost:8001"
  echo "   ✓ API 文档: http://localhost:8001/docs"
else
  echo "   ✗ 后端启动失败，请查看日志: logs/backend.log"
  exit 1
fi
echo ""

# 3. 启动前端
echo "3️⃣ 启动前端服务器 (端口 3002)..."
cd "$PROJECT_ROOT/frontend"

# 后台启动前端
nohup npm start > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!

echo "   前端 PID: $FRONTEND_PID"
echo "   等待前端启动..."
sleep 5

# 检查前端是否启动成功
if lsof -i :3002 > /dev/null 2>&1; then
  echo "   ✓ 前端启动成功: http://localhost:3002"
else
  echo "   ✗ 前端启动失败，请查看日志: logs/frontend.log"
  exit 1
fi
echo ""

# 4. 总结
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 所有服务启动成功！"
echo ""
echo "📝 访问地址:"
echo "   前端应用: http://localhost:3002"
echo "   后端 API: http://localhost:8001"
echo "   API 文档: http://localhost:8001/docs"
echo ""
echo "📊 进程信息:"
echo "   后端 PID: $BACKEND_PID (端口 8001)"
echo "   前端 PID: $FRONTEND_PID (端口 3002)"
echo ""
echo "📄 日志文件:"
echo "   后端日志: logs/backend.log"
echo "   前端日志: logs/frontend.log"
echo ""
echo "🛑 停止服务:"
echo "   运行: ./cleanup.sh"
echo "   或: kill -9 $BACKEND_PID $FRONTEND_PID"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 保存 PID 到文件
mkdir -p "$PROJECT_ROOT/logs"
echo "$BACKEND_PID" > "$PROJECT_ROOT/logs/backend.pid"
echo "$FRONTEND_PID" > "$PROJECT_ROOT/logs/frontend.pid"

# 打开浏览器（可选）
sleep 2
open http://localhost:3002 2>/dev/null || xdg-open http://localhost:3002 2>/dev/null
```

**使用方法**:
```bash
chmod +x start-all.sh
./start-all.sh
```

---

### 方法 3: 使用 tmux 启动（推荐）

```bash
#!/bin/bash
# start-tmux.sh - 使用 tmux 启动项目

SESSION_NAME="genshin_wiki"
PROJECT_ROOT="/Users/anker/Desktop/learn project/Speckit/genshin_wiki_information"

# 检查 tmux 会话是否已存在
if tmux has-session -t $SESSION_NAME 2>/dev/null; then
  echo "会话 '$SESSION_NAME' 已存在"
  echo "附加到现有会话: tmux attach -t $SESSION_NAME"
  echo "或先删除旧会话: tmux kill-session -t $SESSION_NAME"
  exit 1
fi

echo "创建 tmux 会话: $SESSION_NAME"

# 创建新会话并启动后端
tmux new-session -d -s $SESSION_NAME -n backend
tmux send-keys -t $SESSION_NAME:backend "cd '$PROJECT_ROOT/backend'" C-m
tmux send-keys -t $SESSION_NAME:backend "python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload" C-m

# 创建新窗口启动前端
tmux new-window -t $SESSION_NAME -n frontend
tmux send-keys -t $SESSION_NAME:frontend "cd '$PROJECT_ROOT/frontend'" C-m
tmux send-keys -t $SESSION_NAME:frontend "npm start" C-m

# 创建日志监控窗口
tmux new-window -t $SESSION_NAME -n logs
tmux send-keys -t $SESSION_NAME:logs "cd '$PROJECT_ROOT'" C-m

echo ""
echo "✅ tmux 会话创建成功！"
echo ""
echo "附加到会话:"
echo "  tmux attach -t $SESSION_NAME"
echo ""
echo "tmux 快捷键:"
echo "  Ctrl+b 然后按 0/1/2   - 切换窗口"
echo "  Ctrl+b 然后按 d       - 分离会话（后台运行）"
echo "  Ctrl+b 然后按 [       - 进入滚动模式（q 退出）"
echo ""
echo "停止所有服务:"
echo "  tmux kill-session -t $SESSION_NAME"

# 自动附加到会话
tmux attach -t $SESSION_NAME
```

---

## 🔍 故障排查

### 问题 1: 端口已被占用

**症状**: `Address already in use` 错误

**解决**:
```bash
# 找出占用端口的进程
lsof -i :8001
lsof -i :3002

# 杀死进程
kill -9 <PID>

# 或一键清理
lsof -ti :8001 | xargs kill -9
```

### 问题 2: 前端无法连接后端

**症状**: 前端显示 "加载失败" 或 "网络错误"

**检查清单**:
```bash
# 1. 确认后端正在运行
lsof -i :8001

# 2. 测试后端 API
curl http://localhost:8001/api/characters/

# 3. 检查前端代理配置
cat frontend/package.json | grep proxy
# 应该显示: "proxy": "http://localhost:8001"

# 4. 检查前端环境变量
cat frontend/.env | grep API
# 应该显示: REACT_APP_API_BASE_URL=http://localhost:8001/api
```

### 问题 3: 后端返回空响应

**症状**: `curl: (52) Empty reply from server`

**解决**:
```bash
# 1. 重启后端
pkill -9 -f uvicorn
cd backend
python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload

# 2. 检查后端日志
tail -f logs/backend.log  # 如果有日志文件

# 3. 验证 Python 环境
python3 --version
pip list | grep fastapi
```

### 问题 4: 前端编译错误

**症状**: 编译失败或模块未找到

**解决**:
```bash
cd frontend

# 清理缓存
rm -rf node_modules package-lock.json

# 重新安装
npm install

# 重新启动
npm start
```

---

## 📊 监控命令

### 实时监控进程

```bash
# 监控后端进程
watch -n 1 'lsof -i :8001'

# 监控前端进程
watch -n 1 'lsof -i :3002'

# 监控所有项目端口
watch -n 1 'lsof -i :8001 && echo "---" && lsof -i :3002'
```

### 查看日志

```bash
# 后端日志（如果有）
tail -f logs/backend.log

# 前端日志（如果有）
tail -f logs/frontend.log

# 实时监控终端输出
# 在启动服务的终端中查看
```

---

## 📝 常用命令速查表

| 操作 | 命令 |
|------|------|
| 查看后端进程 | `lsof -i :8001` |
| 查看前端进程 | `lsof -i :3002` |
| 杀死后端 | `lsof -ti :8001 \| xargs kill -9` |
| 杀死前端 | `lsof -ti :3002 \| xargs kill -9` |
| 清理所有进程 | `./cleanup.sh` |
| 启动后端 | `cd backend && python3 -m uvicorn src.main:app --host 0.0.0.0 --port 8001 --reload` |
| 启动前端 | `cd frontend && npm start` |
| 一键启动所有 | `./start-all.sh` |
| 测试后端 API | `curl http://localhost:8001/docs` |
| 测试前端 | `curl http://localhost:3002` |

---

## 🎯 推荐工作流

### 日常开发流程

1. **早上开始工作**
   ```bash
   ./cleanup.sh      # 清理昨天的进程
   ./start-all.sh    # 启动所有服务
   ```

2. **开发过程中**
   - 后端代码修改会自动重载（`--reload` 参数）
   - 前端代码修改会热更新（HMR）
   - 无需手动重启

3. **遇到问题时**
   ```bash
   ./cleanup.sh      # 清理进程
   # 分别在两个终端启动后端和前端，便于查看日志
   ```

4. **下班前**
   ```bash
   ./cleanup.sh      # 清理所有进程
   ```

---

**最后更新**: 2025-11-06
**项目**: 原神游戏信息网站
