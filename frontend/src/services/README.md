# Frontend API Service 架构文档

## 概述

本目录包含了前端统一的 API Service 层实现，提供：

- **统一的 HTTP 请求封装**
- **自动错误分类和处理**
- **网络错误自动重试机制**
- **请求/响应拦截**
- **日志记录**
- **请求取消支持**

## 目录结构

```
services/
├── base/                      # 基础服务层
│   ├── BaseAPIService.js      # API 基础类
│   ├── interceptors.js        # 请求/响应拦截器
│   └── retryPolicy.js         # 重试策略
│
├── errors/                    # 错误类定义
│   ├── NetworkError.js        # 网络错误
│   ├── BusinessError.js       # 业务错误
│   ├── SystemError.js         # 系统错误
│   └── index.js               # 错误类导出
│
├── logger/                    # 日志服务（待实现）
│   ├── ErrorLogger.js         # 错误日志记录器
│   ├── RequestLogger.js       # 请求日志记录器
│   └── LoggerConfig.js        # 日志配置
│
├── characterAPI.js            # 角色 API 服务
├── weaponAPI.js               # 武器 API 服务
├── artifactAPI.js             # 圣遗物 API 服务
├── monsterAPI.js              # 怪物 API 服务
└── searchAPI.js               # 搜索 API 服务
```

## 快速开始

### 1. 基础使用

```javascript
import characterAPI from '@/services/characterAPI';

// 获取角色列表
async function fetchCharacters() {
  try {
    const result = await characterAPI.getCharacterList({
      element: '火',
      rarity: 5,
      page: 1,
      per_page: 20
    });

    console.log('角色列表:', result.characters);
    console.log('总数:', result.total);
  } catch (error) {
    // 错误已经被统一处理，这里可以做额外的 UI 提示
    console.error('获取角色失败:', error.getUserMessage());
  }
}
```

### 2. 错误处理

```javascript
import characterAPI from '@/services/characterAPI';
import { NetworkError, BusinessError, SystemError } from '@/services/errors';

async function handleCharacterOperation() {
  try {
    const character = await characterAPI.getCharacterDetail(123);
    // 处理成功结果
  } catch (error) {
    if (error instanceof NetworkError) {
      // 网络错误 - 已自动重试失败
      showNotification('网络连接失败，请检查网络设置', 'error');
    } else if (error instanceof BusinessError) {
      // 业务错误 - 显示具体错误信息
      if (error.isNotFoundError()) {
        showNotification('角色不存在', 'warning');
      } else if (error.isValidationError()) {
        // 显示字段级错误
        const fieldErrors = error.getFieldErrors();
        showFormErrors(fieldErrors);
      } else {
        showNotification(error.getUserMessage(), 'warning');
      }
    } else if (error instanceof SystemError) {
      // 系统错误 - 显示通用错误
      showNotification('系统繁忙，请稍后重试', 'error');
      // 可以记录错误日志用于监控
      logErrorToServer(error.getDetails());
    }
  }
}
```

### 3. 创建新的 API 服务

```javascript
// weaponAPI.js
import BaseAPIService from './base/BaseAPIService';

class WeaponAPIService extends BaseAPIService {
  constructor() {
    super('/api'); // 设置 baseURL
  }

  /**
   * 获取武器列表
   */
  async getWeaponList(filters = {}) {
    try {
      const response = await this.get('/weapons/', filters);
      return response.data || response;
    } catch (error) {
      console.error('获取武器列表失败:', error);
      throw error;
    }
  }

  /**
   * 获取武器详情
   */
  async getWeaponDetail(id) {
    if (!id) {
      throw new Error('武器 ID 不能为空');
    }

    try {
      const response = await this.get(`/weapons/${id}`);
      return response.data || response;
    } catch (error) {
      console.error(`获取武器详情失败 (ID: ${id}):`, error);
      throw error;
    }
  }

  // 更多方法...
}

// 导出单例
const weaponAPI = new WeaponAPIService();
export default weaponAPI;
```

## 核心概念

### BaseAPIService

所有 API 服务的基类，提供：

- `get(url, params, config)` - GET 请求
- `post(url, data, config)` - POST 请求
- `put(url, data, config)` - PUT 请求
- `patch(url, data, config)` - PATCH 请求
- `delete(url, config)` - DELETE 请求
- `upload(url, formData, onProgress)` - 文件上传
- `batchRequest(requests)` - 批量并行请求
- `cancelRequest(message)` - 取消请求

**特性：**
- 自动添加 baseURL
- 请求/响应拦截
- 错误统一处理
- 网络错误自动重试
- 请求日志记录

### 错误分类

#### NetworkError（网络错误）
- **触发条件**：网络连接失败、请求超时、DNS 解析失败
- **处理策略**：自动重试（最多 3 次，指数退避）
- **用户提示**："网络连接失败，请检查网络设置"

#### BusinessError（业务错误）
- **触发条件**：HTTP 4xx 状态码
- **子类型**：
  - ValidationError (400) - 参数验证失败
  - AuthenticationError (401) - 认证失败
  - PermissionError (403) - 权限不足
  - NotFoundError (404) - 资源不存在
  - ConflictError (409) - 资源冲突
- **处理策略**：不自动重试，显示具体错误信息
- **用户提示**：根据具体错误显示详细信息

#### SystemError（系统错误）
- **触发条件**：HTTP 5xx 状态码
- **处理策略**：记录日志，不暴露技术细节
- **用户提示**："系统繁忙，请稍后重试"

### 重试策略

使用指数退避算法的自动重试机制：

```javascript
// 默认配置
{
  maxRetries: 3,          // 最大重试次数
  initialDelay: 1000,     // 初始延迟 1 秒
  maxDelay: 10000,        // 最大延迟 10 秒
  backoffFactor: 2        // 每次延迟翻倍
}

// 预设配置
import { RETRY_PRESETS } from './base/retryPolicy';

// 快速重试（适合轻量级请求）
RETRY_PRESETS.FAST

// 标准重试（默认）
RETRY_PRESETS.STANDARD

// 持久重试（适合重要请求）
RETRY_PRESETS.PERSISTENT

// 无重试
RETRY_PRESETS.NONE
```

### 拦截器

#### 请求拦截器
自动添加：
- 请求 ID (`X-Request-ID`)
- 时间戳 (`X-Request-Time`)
- 认证 token (`Authorization`)
- 请求日志

#### 响应拦截器
自动处理：
- 统一响应格式转换
- 错误分类
- 特殊状态码处理（401/403/404/429）
- 响应日志

## React 组件中的使用

### 基础用法

```javascript
import React, { useState, useEffect } from 'react';
import characterAPI from '@/services/characterAPI';
import { getUserMessage } from '@/services/errors';

function CharacterList() {
  const [characters, setCharacters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchData() {
      try {
        setLoading(true);
        setError(null);

        const result = await characterAPI.getCharacterList();
        setCharacters(result.characters);
      } catch (err) {
        setError(getUserMessage(err));
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  if (loading) return <div>加载中...</div>;
  if (error) return <div>错误：{error}</div>;

  return (
    <div>
      {characters.map(char => (
        <div key={char.id}>{char.name}</div>
      ))}
    </div>
  );
}
```

### 使用自定义 Hook

```javascript
// hooks/useCharacterList.js
import { useState, useEffect } from 'react';
import characterAPI from '@/services/characterAPI';
import { getUserMessage } from '@/services/errors';

export function useCharacterList(filters = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);

      const result = await characterAPI.getCharacterList(filters);
      setData(result);
    } catch (err) {
      setError(getUserMessage(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [JSON.stringify(filters)]);

  return {
    characters: data?.characters || [],
    total: data?.total || 0,
    loading,
    error,
    refetch: fetchData
  };
}

// 使用
function CharacterListPage() {
  const { characters, loading, error, refetch } = useCharacterList({
    element: '火'
  });

  // ...
}
```

## 高级用法

### 1. 请求取消

```javascript
import characterAPI from '@/services/characterAPI';

// 创建取消 token
const cancelToken = characterAPI.getCancelToken();

// 发送可取消的请求
characterAPI.get('/characters/', {}, { cancelToken })
  .then(data => console.log(data))
  .catch(error => {
    if (axios.isCancel(error)) {
      console.log('请求已取消');
    }
  });

// 取消请求
characterAPI.cancelRequest('用户取消');
```

### 2. 批量请求

```javascript
import characterAPI from '@/services/characterAPI';

// 批量请求（并行，全部成功）
const results = await characterAPI.batchRequest([
  { method: 'GET', url: '/characters/1' },
  { method: 'GET', url: '/characters/2' },
  { method: 'GET', url: '/characters/3' }
]);

// 批量请求（并行，允许部分失败）
const results = await characterAPI.batchRequestAllSettled([
  { method: 'GET', url: '/characters/1' },
  { method: 'GET', url: '/characters/invalid' }, // 这个会失败
  { method: 'GET', url: '/characters/3' }
]);

results.forEach((result, index) => {
  if (result.status === 'fulfilled') {
    console.log(`请求 ${index} 成功:`, result.value);
  } else {
    console.log(`请求 ${index} 失败:`, result.reason);
  }
});
```

### 3. 文件上传

```javascript
import characterAPI from '@/services/characterAPI';

// 上传文件
const formData = new FormData();
formData.append('file', file);

await characterAPI.upload(
  '/images/upload',
  formData,
  (progress) => {
    console.log(`上传进度: ${progress}%`);
  }
);
```

## 最佳实践

### 1. 错误处理

✅ **推荐**：使用错误类的工具方法
```javascript
import { getUserMessage, getErrorDetails } from '@/services/errors';

try {
  await characterAPI.getCharacterDetail(id);
} catch (error) {
  // 显示用户友好的错误信息
  showNotification(getUserMessage(error), 'error');

  // 记录详细的错误日志
  console.error('详细错误:', getErrorDetails(error));
}
```

❌ **不推荐**：直接使用 error.message
```javascript
try {
  await characterAPI.getCharacterDetail(id);
} catch (error) {
  // 可能暴露技术细节
  showNotification(error.message, 'error');
}
```

### 2. 参数验证

✅ **推荐**：在 API 方法中进行参数验证
```javascript
async getCharacterDetail(id) {
  if (!id) {
    throw new Error('角色 ID 不能为空');
  }
  // ...
}
```

### 3. 单例模式

✅ **推荐**：导出 API 服务的单例
```javascript
const characterAPI = new CharacterAPIService();
export default characterAPI;
```

### 4. 方法命名

✅ **推荐**：使用清晰的动词前缀
- `get...()` - 获取单个资源
- `list...()` 或 `get...List()` - 获取列表
- `create...()` - 创建资源
- `update...()` - 更新资源
- `delete...()` - 删除资源
- `search...()` - 搜索资源

## 测试

```javascript
// characterAPI.test.js
import characterAPI from './characterAPI';
import { NetworkError, BusinessError } from './errors';

describe('CharacterAPI', () => {
  describe('getCharacterList', () => {
    it('should return character list', async () => {
      const result = await characterAPI.getCharacterList();
      expect(result).toHaveProperty('characters');
      expect(result).toHaveProperty('total');
    });

    it('should handle network error', async () => {
      // Mock 网络错误
      await expect(
        characterAPI.getCharacterList()
      ).rejects.toThrow(NetworkError);
    });
  });
});
```

## 迁移指南

### 从旧架构迁移

**旧代码：**
```javascript
// 直接使用 axios
import axios from 'axios';

async function getCharacters() {
  try {
    const response = await axios.get('/api/characters/');
    return response.data;
  } catch (error) {
    console.error(error);
    throw error;
  }
}
```

**新代码：**
```javascript
// 使用 characterAPI
import characterAPI from '@/services/characterAPI';

async function getCharacters() {
  try {
    const result = await characterAPI.getCharacterList();
    return result.characters;
  } catch (error) {
    // 错误已经被分类和处理
    throw error;
  }
}
```

## 配置

### 环境变量

```bash
# .env.development
REACT_APP_API_BASE_URL=http://localhost:8000/api

# .env.production
REACT_APP_API_BASE_URL=https://api.yourdomain.com/api
```

### 自定义配置

```javascript
// 创建自定义配置的 API 服务
import BaseAPIService from './base/BaseAPIService';

class CustomAPIService extends BaseAPIService {
  constructor() {
    super('/api/v2', 60000); // 自定义 baseURL 和 timeout
  }
}
```

## 常见问题

### Q: 如何禁用自动重试？

```javascript
// 在请求配置中设置
await characterAPI.get('/characters/', {}, {
  retry: false
});
```

### Q: 如何自定义错误提示？

```javascript
import { getUserMessage } from '@/services/errors';

try {
  await characterAPI.getCharacterDetail(id);
} catch (error) {
  const message = getUserMessage(error);
  // 使用自定义的通知组件
  customNotification.show(message);
}
```

### Q: 如何添加自定义请求头？

```javascript
await characterAPI.get('/characters/', {}, {
  headers: {
    'X-Custom-Header': 'value'
  }
});
```

## 下一步

- [ ] 实现 ErrorLogger 日志服务
- [ ] 添加性能监控
- [ ] 实现请求缓存
- [ ] 添加请求队列管理
- [ ] 支持 GraphQL

## 相关资源

- [Axios 文档](https://axios-http.com/)
- [项目规格文档](../../specs/001-genshin-info-website/spec.md)
- [架构设计文档](../../specs/001-genshin-info-website/plan.md)
