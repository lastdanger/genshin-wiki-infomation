# API 错误处理文档

本文档说明原神游戏信息网站 API 的错误处理机制和错误响应格式。

## 目录

- [错误响应格式](#错误响应格式)
- [错误代码](#错误代码)
- [HTTP 状态码](#http-状态码)
- [错误示例](#错误示例)
- [最佳实践](#最佳实践)

## 错误响应格式

所有错误响应都遵循统一的 JSON 格式：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {},
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters/123",
    "request_id": "abc123"
  }
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `success` | boolean | 始终为 `false` |
| `error.code` | string | 错误代码，用于程序化处理 |
| `error.message` | string | 人类可读的错误描述 |
| `error.details` | object/array | 错误详细信息（可选） |
| `error.timestamp` | string | 错误发生时间（ISO 8601格式） |
| `error.path` | string | 请求的API路径 |
| `error.request_id` | string | 请求追踪ID（可选，仅服务器错误） |

## 错误代码

### 客户端错误 (4xx)

#### VALIDATION_ERROR (422)
数据验证失败

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求数据验证失败",
    "details": [
      {
        "field": "element",
        "message": "Invalid element type. Must be one of: Pyro, Hydro, Anemo, Electro, Dendro, Cryo, Geo",
        "type": "value_error.enum"
      }
    ],
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters"
  }
}
```

**触发场景：**
- 必填字段缺失
- 字段类型不正确
- 字段值不符合约束条件
- 枚举值不在允许范围内

#### NOT_FOUND (404)
资源未找到

```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "角色未找到: 999",
    "details": {
      "resource": "Character",
      "id": 999
    },
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters/999"
  }
}
```

**触发场景：**
- 请求的资源ID不存在
- API端点不存在

#### BAD_REQUEST (400)
请求格式错误

```json
{
  "success": false,
  "error": {
    "code": "BAD_REQUEST",
    "message": "请求格式错误",
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters"
  }
}
```

**触发场景：**
- JSON格式错误
- 请求体为空但需要数据
- 查询参数格式错误

#### UNAUTHORIZED (401)
未授权访问

```json
{
  "success": false,
  "error": {
    "code": "UNAUTHORIZED",
    "message": "需要身份验证",
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/admin/characters"
  }
}
```

**触发场景：**
- 缺少认证令牌
- 认证令牌过期或无效

#### FORBIDDEN (403)
权限不足

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "无权限执行操作: delete on Character",
    "details": {
      "action": "delete",
      "resource": "Character"
    },
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters/123"
  }
}
```

**触发场景：**
- 用户权限不足
- 尝试访问受限资源

#### CONFLICT (409)
资源冲突

```json
{
  "success": false,
  "error": {
    "code": "CONFLICT",
    "message": "角色名称已存在",
    "details": {
      "resource": "Character",
      "field": "name",
      "value": "Diluc"
    },
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters"
  }
}
```

**触发场景：**
- 唯一约束冲突
- 资源已存在
- 并发更新冲突

#### RATE_LIMIT_EXCEEDED (429)
请求频率超限

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "请求频率超限，限制为每分钟100次",
    "details": {
      "limit": 100,
      "window": "分钟"
    },
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters"
  }
}
```

**触发场景：**
- 超过速率限制

### 服务器错误 (5xx)

#### INTERNAL_SERVER_ERROR (500)
服务器内部错误

```json
{
  "success": false,
  "error": {
    "code": "INTERNAL_SERVER_ERROR",
    "message": "服务器内部错误，我们正在处理此问题",
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters",
    "request_id": "a1b2c3d4"
  }
}
```

**触发场景：**
- 未预期的程序错误
- 代码逻辑错误

**注意：** 500错误会包含 `request_id`，用于错误追踪和问题诊断。

#### DATABASE_ERROR (500)
数据库错误

```json
{
  "success": false,
  "error": {
    "code": "DATABASE_ERROR",
    "message": "数据库操作失败，请稍后重试",
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters",
    "request_id": "a1b2c3d4"
  }
}
```

**触发场景：**
- 数据库连接失败
- SQL执行错误
- 事务失败

#### SERVICE_UNAVAILABLE (503)
服务不可用

```json
{
  "success": false,
  "error": {
    "code": "EXTERNAL_API_ERROR",
    "message": "外部API调用失败",
    "details": {
      "api_name": "Genshin Data API",
      "endpoint": "/characters"
    },
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/sync/characters"
  }
}
```

**触发场景：**
- 外部服务不可用
- 依赖服务超时

## HTTP 状态码

| 状态码 | 说明 | 常见错误代码 |
|--------|------|--------------|
| 400 | 请求错误 | BAD_REQUEST, FILE_UPLOAD_ERROR |
| 401 | 未授权 | UNAUTHORIZED |
| 403 | 禁止访问 | PERMISSION_DENIED |
| 404 | 未找到 | NOT_FOUND |
| 409 | 冲突 | CONFLICT |
| 422 | 验证错误 | VALIDATION_ERROR |
| 429 | 频率超限 | RATE_LIMIT_EXCEEDED |
| 500 | 服务器错误 | INTERNAL_SERVER_ERROR, DATABASE_ERROR, DATA_SYNC_ERROR |
| 503 | 服务不可用 | EXTERNAL_API_ERROR |

## 错误示例

### 示例 1: 参数验证失败

**请求：**
```http
GET /api/v1/characters?page=-1&per_page=1000
```

**响应：** (422 Unprocessable Entity)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求数据验证失败",
    "details": [
      {
        "field": "page",
        "message": "ensure this value is greater than or equal to 1",
        "type": "value_error.number.not_ge"
      },
      {
        "field": "per_page",
        "message": "ensure this value is less than or equal to 100",
        "type": "value_error.number.not_le"
      }
    ],
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters"
  }
}
```

### 示例 2: 资源不存在

**请求：**
```http
GET /api/v1/characters/999999
```

**响应：** (404 Not Found)
```json
{
  "success": false,
  "error": {
    "code": "NOT_FOUND",
    "message": "角色未找到: 999999",
    "details": {
      "resource": "Character",
      "id": 999999
    },
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters/999999"
  }
}
```

### 示例 3: 创建时数据验证失败

**请求：**
```http
POST /api/v1/characters
Content-Type: application/json

{
  "name": "",
  "element": "Fire",
  "rarity": 6
}
```

**响应：** (422 Unprocessable Entity)
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "请求数据验证失败",
    "details": [
      {
        "field": "name",
        "message": "ensure this value has at least 1 characters",
        "type": "value_error.any_str.min_length"
      },
      {
        "field": "element",
        "message": "value is not a valid enumeration member; permitted: 'Pyro', 'Hydro', 'Anemo', 'Electro', 'Dendro', 'Cryo', 'Geo'",
        "type": "type_error.enum"
      },
      {
        "field": "rarity",
        "message": "ensure this value is less than or equal to 5",
        "type": "value_error.number.not_le"
      }
    ],
    "timestamp": "2025-11-07T12:00:00Z",
    "path": "/api/v1/characters"
  }
}
```

## 最佳实践

### 1. 检查 `success` 字段

始终先检查响应的 `success` 字段来判断请求是否成功：

```javascript
async function fetchCharacter(id) {
  const response = await fetch(`/api/v1/characters/${id}`);
  const data = await response.json();

  if (data.success) {
    return data.data;
  } else {
    throw new Error(data.error.message);
  }
}
```

### 2. 根据错误代码处理

使用 `error.code` 来进行程序化错误处理：

```javascript
try {
  const character = await createCharacter(data);
} catch (error) {
  switch (error.code) {
    case 'VALIDATION_ERROR':
      // 显示表单验证错误
      showValidationErrors(error.details);
      break;
    case 'CONFLICT':
      // 显示资源冲突提示
      showConflictMessage(error.message);
      break;
    case 'NOT_FOUND':
      // 显示404页面
      show404Page();
      break;
    default:
      // 显示通用错误消息
      showErrorToast(error.message);
  }
}
```

### 3. 提取验证错误详情

对于验证错误，提取详细信息以显示字段级错误：

```javascript
function handleValidationError(errorResponse) {
  const fieldErrors = {};

  errorResponse.error.details.forEach(detail => {
    fieldErrors[detail.field] = detail.message;
  });

  // 在表单中显示错误
  displayFieldErrors(fieldErrors);
}
```

### 4. 保存 request_id

对于服务器错误，保存 `request_id` 以便问题追踪：

```javascript
if (error.code === 'INTERNAL_SERVER_ERROR') {
  console.error('Server error, request ID:', error.request_id);
  reportErrorToMonitoring({
    message: error.message,
    requestId: error.request_id,
    path: error.path,
    timestamp: error.timestamp
  });
}
```

### 5. 友好的用户提示

将技术性错误消息转换为用户友好的提示：

```javascript
const USER_FRIENDLY_MESSAGES = {
  'DATABASE_ERROR': '数据库暂时无法访问，请稍后重试',
  'EXTERNAL_API_ERROR': '数据同步服务暂时不可用',
  'RATE_LIMIT_EXCEEDED': '您的请求过于频繁，请稍后再试',
  'INTERNAL_SERVER_ERROR': '服务暂时出现问题，我们正在修复'
};

function getUserFriendlyMessage(error) {
  return USER_FRIENDLY_MESSAGES[error.code] || error.message;
}
```

### 6. 重试策略

对于某些错误类型，实现自动重试：

```javascript
async function fetchWithRetry(url, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const response = await fetch(url);
      const data = await response.json();

      if (data.success) {
        return data;
      }

      // 对于某些错误不重试
      if (['VALIDATION_ERROR', 'NOT_FOUND', 'FORBIDDEN'].includes(data.error.code)) {
        throw new Error(data.error.message);
      }

      // 等待后重试
      await sleep(1000 * Math.pow(2, i));
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

## 联系支持

如果遇到包含 `request_id` 的错误，请联系技术支持并提供以下信息：

- Request ID
- 错误时间
- API路径
- 操作描述

**支持渠道：**
- Email: support@genshin-wiki.com
- Issues: https://github.com/lastdanger/genshin-wiki-infomation/issues
