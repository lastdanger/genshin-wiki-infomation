/**
 * Axios 拦截器配置（TypeScript 版本）
 *
 * 包含请求拦截器和响应拦截器，提供：
 * - 请求前的统一处理（添加 token、请求 ID 等）
 * - 响应后的统一处理（数据转换、错误处理）
 * - 集成新的错误处理系统
 */

import { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import { ErrorHandler, ApiError } from '../errors';

/**
 * 生成请求ID
 */
function generateRequestId(): string {
  return 'req-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

/**
 * 设置 axios 拦截器
 */
export function setupInterceptors(axiosInstance: AxiosInstance): void {
  // 请求拦截器
  axiosInstance.interceptors.request.use(
    (config) => requestInterceptor(config),
    (error) => Promise.reject(error)
  );

  // 响应拦截器
  axiosInstance.interceptors.response.use(
    (response) => responseSuccessInterceptor(response),
    (error) => responseErrorInterceptor(error)
  );
}

/**
 * 请求拦截器
 * 在请求发送前执行
 */
function requestInterceptor(config: AxiosRequestConfig): AxiosRequestConfig {
  // 添加请求 ID（用于追踪和日志）
  if (config.headers) {
    config.headers['X-Request-ID'] = generateRequestId();
    config.headers['X-Request-Time'] = new Date().toISOString();

    // 添加认证 token（如果存在）
    const token = getAuthToken();
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
  }

  // 记录请求日志（开发环境）
  if (process.env.NODE_ENV === 'development') {
    console.log('[API Request]', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
    });
  }

  return config;
}

/**
 * 响应成功拦截器
 * 在收到成功响应后执行
 */
function responseSuccessInterceptor(response: AxiosResponse): AxiosResponse {
  const { data, status, config } = response;

  // 记录响应日志（开发环境）
  if (process.env.NODE_ENV === 'development') {
    console.log('[API Response]', {
      method: config.method?.toUpperCase(),
      url: config.url,
      status,
      success: data?.success,
    });
  }

  // 检查是否是标准的成功响应
  if (data && typeof data === 'object' && data.success === false) {
    // 后端返回了错误响应，但HTTP状态码是2xx
    // 这种情况也应该作为错误处理
    const apiError = ErrorHandler.handle(new Error(data.error?.message || '请求失败'), {
      logToConsole: false,
    });
    return Promise.reject(apiError);
  }

  return response;
}

/**
 * 响应错误拦截器
 * 在请求失败或响应错误时执行
 */
async function responseErrorInterceptor(error: AxiosError): Promise<never> {
  const { config, response } = error;

  // 使用 ErrorHandler 统一处理错误
  const apiError = ErrorHandler.handle(error, {
    logToConsole: true,
    reportToService: process.env.NODE_ENV === 'production',
  });

  // 记录错误日志
  if (process.env.NODE_ENV === 'development') {
    console.error('[API Error]', {
      method: config?.method?.toUpperCase(),
      url: config?.url,
      status: response?.status,
      code: apiError.code,
      message: apiError.message,
      details: apiError.details,
    });
  }

  // 处理特殊的 HTTP 状态码
  if (response) {
    await handleSpecialStatusCodes(response.status, apiError);
  }

  // 拒绝 Promise，返回 ApiError
  return Promise.reject(apiError);
}

/**
 * 处理特殊的 HTTP 状态码
 */
async function handleSpecialStatusCodes(status: number, error: ApiError): Promise<void> {
  switch (status) {
    case 401:
      // 认证失败，清除 token
      await handleAuthenticationError();
      break;

    case 403:
      // 权限不足
      handlePermissionError(error);
      break;

    case 404:
      // 资源不存在（通常不需要特殊处理）
      break;

    case 429:
      // 请求过于频繁
      handleRateLimitError(error);
      break;

    default:
      break;
  }
}

/**
 * 获取认证 token
 */
function getAuthToken(): string | null {
  try {
    return localStorage.getItem('authToken');
  } catch (error) {
    console.error('获取 token 失败:', error);
    return null;
  }
}

/**
 * 处理认证错误（401）
 */
async function handleAuthenticationError(): Promise<void> {
  // 清除本地 token
  localStorage.removeItem('authToken');
  localStorage.removeItem('userInfo');

  // 发送自定义事件，让应用监听并处理
  window.dispatchEvent(new CustomEvent('auth:logout', {
    detail: { reason: 'unauthorized' }
  }));

  // TODO: 根据实际需求决定是否自动跳转到登录页
  // window.location.href = '/login';
}

/**
 * 处理权限错误（403）
 */
function handlePermissionError(error: ApiError): void {
  // 发送自定义事件
  window.dispatchEvent(new CustomEvent('error:permission', {
    detail: { error }
  }));
}

/**
 * 处理频率限制错误（429）
 */
function handleRateLimitError(error: ApiError): void {
  // 发送自定义事件
  window.dispatchEvent(new CustomEvent('error:rateLimit', {
    detail: { error }
  }));
}

/**
 * 导出拦截器函数
 */
export default {
  setupInterceptors,
  requestInterceptor,
  responseSuccessInterceptor,
  responseErrorInterceptor,
};
