# 前端错误处理文档

本文档说明原神游戏信息网站前端的错误处理机制和使用方法。

## 目录

- [概述](#概述)
- [错误类型](#错误类型)
- [ErrorBoundary 使用](#errorboundary-使用)
- [Axios 拦截器](#axios-拦截器)
- [useErrorHandler Hook](#useerrorhandler-hook)
- [Toast 提示](#toast-提示)
- [最佳实践](#最佳实践)

## 概述

前端错误处理系统提供：

1. **ErrorBoundary** - 捕获 React 组件树中的错误
2. **统一错误类** - ApiError 及其子类
3. **Axios 拦截器** - 自动处理 API 错误
4. **useErrorHandler Hook** - React 组件中的错误处理
5. **Toast 组件** - 用户友好的错误提示

## 错误类型

### ErrorCode 枚举

```typescript
enum ErrorCode {
  // 网络错误
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',

  // 客户端错误 (4xx)
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  NOT_FOUND = 'NOT_FOUND',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',

  // 服务器错误 (5xx)
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
}
```

### ApiError 类

```typescript
class ApiError extends Error {
  code: ErrorCode;
  severity: ErrorSeverity;
  details?: ErrorDetail[];
  requestId?: string;
  statusCode?: number;
}
```

## ErrorBoundary 使用

### 基本用法

```tsx
import { ErrorBoundary } from './components/ErrorBoundary';

function App() {
  return (
    <ErrorBoundary>
      <YourApp />
    </ErrorBoundary>
  );
}
```

### 自定义错误处理

```tsx
<ErrorBoundary
  onError={(error, errorInfo) => {
    // 自定义错误处理
    console.log('Error caught:', error);
  }}
  fallback={<CustomErrorPage />}
>
  <YourComponent />
</ErrorBoundary>
```

### 使用 resetKeys

```tsx
function UserProfile({ userId }) {
  return (
    <ErrorBoundary resetKeys={[userId]}>
      <ProfileContent userId={userId} />
    </ErrorBoundary>
  );
}
```

当 `userId` 变化时，ErrorBoundary 会自动重置错误状态。

## Axios 拦截器

Axios 拦截器自动处理所有 API 错误，无需手动处理。

### 配置

```typescript
import axios from 'axios';
import { setupInterceptors } from './services/base/interceptors';

const api = axios.create({
  baseURL: process.env.REACT_APP_API_URL,
  timeout: 10000,
});

// 设置拦截器
setupInterceptors(api);
```

### 自动处理

拦截器会自动：
- 将 Axios 错误转换为 ApiError
- 记录错误日志
- 处理特殊状态码（401, 403, 429 等）
- 触发自定义事件

## useErrorHandler Hook

### 基本用法

```tsx
import { useErrorHandler } from './hooks/useErrorHandler';

function CharacterList() {
  const { error, handleError, clearError } = useErrorHandler({
    showToast: true,
  });

  const fetchCharacters = async () => {
    try {
      const response = await api.get('/characters');
      return response.data;
    } catch (err) {
      handleError(err);
    }
  };

  return (
    <div>
      {error && (
        <div className="error-message">
          {error.message}
          <button onClick={clearError}>关闭</button>
        </div>
      )}
      {/* ... */}
    </div>
  );
}
```

### 使用 useAsyncError

```tsx
import { useAsyncError } from './hooks/useErrorHandler';

function CharacterDetail({ id }) {
  const fetchCharacter = async (id) => {
    const response = await api.get(`/characters/${id}`);
    return response.data;
  };

  const { execute, loading, error, data } = useAsyncError(fetchCharacter);

  useEffect(() => {
    execute(id);
  }, [id]);

  if (loading) return <Loading />;
  if (error) return <ErrorMessage error={error} />;
  if (!data) return null;

  return <CharacterCard character={data} />;
}
```

## Toast 提示

### 添加 ToastContainer

在应用根组件中添加：

```tsx
import { ToastContainer } from './components/UI/Toast';

function App() {
  return (
    <>
      <ErrorBoundary>
        <YourApp />
      </ErrorBoundary>
      <ToastContainer />
    </>
  );
}
```

### 手动显示 Toast

```typescript
// 通过自定义事件触发
window.dispatchEvent(new CustomEvent('toast:show', {
  detail: {
    type: 'error',
    message: '操作失败，请重试',
    duration: 5000,
  },
}));
```

### 通过 useErrorHandler 自动显示

```tsx
const { handleError } = useErrorHandler({
  showToast: true, // 默认为 true
});

// 错误会自动显示 Toast
try {
  await someAsyncOperation();
} catch (err) {
  handleError(err); // 自动显示 Toast
}
```

## 最佳实践

### 1. 分层错误处理

```tsx
// 全局层 - ErrorBoundary
<ErrorBoundary>
  <App />
</ErrorBoundary>

// 路由层 - 每个路由有独立的 ErrorBoundary
<Route path="/characters">
  <ErrorBoundary>
    <CharacterList />
  </ErrorBoundary>
</Route>

// 组件层 - useErrorHandler
function CharacterList() {
  const { error, handleError } = useErrorHandler();
  // ...
}
```

### 2. 友好的错误消息

```typescript
import { getUserFriendlyMessage } from './services/errors';

function ErrorDisplay({ error }) {
  const message = getUserFriendlyMessage(error);
  return <div className="error">{message}</div>;
}
```

### 3. 错误重试

```tsx
function DataFetcher() {
  const [retryCount, setRetryCount] = useState(0);
  const { error, handleError, clearError } = useErrorHandler();

  const fetchData = async () => {
    try {
      const data = await api.get('/data');
      return data;
    } catch (err) {
      const apiError = handleError(err);

      // 判断是否可以重试
      if (isRetryable(apiError) && retryCount < 3) {
        setTimeout(() => {
          setRetryCount(c => c + 1);
          clearError();
          fetchData();
        }, 1000 * Math.pow(2, retryCount)); // 指数退避
      }
    }
  };

  return (
    <div>
      {error && (
        <button onClick={() => {
          clearError();
          fetchData();
        }}>
          重试
        </button>
      )}
    </div>
  );
}
```

### 4. 处理认证错误

```typescript
// 监听认证错误事件
useEffect(() => {
  const handleAuthError = () => {
    // 跳转到登录页
    navigate('/login', {
      state: { from: location.pathname }
    });
  };

  window.addEventListener('auth:logout', handleAuthError);
  return () => window.removeEventListener('auth:logout', handleAuthError);
}, []);
```

### 5. 开发环境 vs 生产环境

```typescript
const isDevelopment = process.env.NODE_ENV === 'development';

if (isDevelopment) {
  // 显示详细错误信息
  console.error('Detailed error:', error);
} else {
  // 只显示友好消息
  showToast(getUserFriendlyMessage(error));
  // 报告到监控服务
  ErrorHandler.reportError(error);
}
```

### 6. 表单验证错误

```tsx
function CharacterForm() {
  const { handleError } = useErrorHandler({ showToast: false });
  const [fieldErrors, setFieldErrors] = useState({});

  const handleSubmit = async (data) => {
    try {
      await api.post('/characters', data);
    } catch (err) {
      const apiError = handleError(err);

      // 处理验证错误
      if (apiError.code === ErrorCode.VALIDATION_ERROR && apiError.details) {
        const errors = {};
        apiError.details.forEach(detail => {
          if (detail.field) {
            errors[detail.field] = detail.message;
          }
        });
        setFieldErrors(errors);
      }
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input name="name" />
      {fieldErrors.name && (
        <span className="error">{fieldErrors.name}</span>
      )}
      {/* ... */}
    </form>
  );
}
```

### 7. 全局错误监听

```tsx
// 在根组件中监听全局错误事件
useEffect(() => {
  // 监听权限错误
  const handlePermissionError = (event) => {
    const { error } = event.detail;
    showModal({
      title: '权限不足',
      message: '您没有权限执行此操作',
    });
  };

  // 监听频率限制错误
  const handleRateLimitError = (event) => {
    const { error } = event.detail;
    showModal({
      title: '请求过于频繁',
      message: '请稍后再试',
    });
  };

  window.addEventListener('error:permission', handlePermissionError);
  window.addEventListener('error:rateLimit', handleRateLimitError);

  return () => {
    window.removeEventListener('error:permission', handlePermissionError);
    window.removeEventListener('error:rateLimit', handleRateLimitError);
  };
}, []);
```

## 错误代码映射

| HTTP Status | ErrorCode | 用户提示 |
|-------------|-----------|----------|
| - | NETWORK_ERROR | 网络连接失败，请检查您的网络设置 |
| - | TIMEOUT_ERROR | 请求超时，请稍后重试 |
| 400 | BAD_REQUEST | 请求参数错误，请检查输入 |
| 401 | UNAUTHORIZED | 身份验证失败，请重新登录 |
| 403 | FORBIDDEN | 您没有权限执行此操作 |
| 404 | NOT_FOUND | 请求的资源不存在 |
| 409 | CONFLICT | 操作冲突，请刷新页面后重试 |
| 422 | VALIDATION_ERROR | 输入数据验证失败 |
| 429 | RATE_LIMIT_EXCEEDED | 请求过于频繁，请稍后再试 |
| 500 | INTERNAL_SERVER_ERROR | 服务器错误，我们正在处理 |
| 503 | SERVICE_UNAVAILABLE | 服务暂时不可用，请稍后重试 |

## 技术支持

如遇问题，请联系：
- Email: support@genshin-wiki.com
- Issues: https://github.com/lastdanger/genshin-wiki-infomation/issues
