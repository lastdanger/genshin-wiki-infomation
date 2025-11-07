/**
 * Axios拦截器配置
 *
 * 包含请求拦截器和响应拦截器，提供：
 * - 请求前的统一处理（添加token、请求ID等）
 * - 响应后的统一处理（数据转换、错误处理）
 */

// 简单的UUID生成函数（避免额外依赖）
function generateRequestId() {
  return 'req-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
}

/**
 * 设置axios拦截器
 *
 * @param {Object} axiosInstance - axios实例
 */
export function setupInterceptors(axiosInstance) {
  // 请求拦截器
  axiosInstance.interceptors.request.use(
    (config) => {
      return requestInterceptor(config);
    },
    (error) => {
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  axiosInstance.interceptors.response.use(
    (response) => {
      return responseSuccessInterceptor(response);
    },
    (error) => {
      return responseErrorInterceptor(error);
    }
  );
}

/**
 * 请求拦截器
 * 在请求发送前执行
 *
 * @param {Object} config - axios请求配置
 * @returns {Object} - 修改后的配置
 */
function requestInterceptor(config) {
  // 添加请求ID（用于追踪和日志）
  config.headers['X-Request-ID'] = generateRequestId();

  // 添加时间戳
  config.headers['X-Request-Time'] = new Date().toISOString();

  // 添加认证token（如果存在）
  const token = getAuthToken();
  if (token) {
    config.headers['Authorization'] = `Bearer ${token}`;
  }

  // 记录请求日志（开发环境）
  if (process.env.NODE_ENV === 'development') {
    console.log('[API Request]', {
      method: config.method?.toUpperCase(),
      url: config.url,
      params: config.params,
      data: config.data,
      headers: config.headers
    });
  }

  return config;
}

/**
 * 响应成功拦截器
 * 在收到成功响应后执行
 *
 * @param {Object} response - axios响应对象
 * @returns {Object} - 修改后的响应
 */
function responseSuccessInterceptor(response) {
  const { data, status, config } = response;

  // 记录响应日志（开发环境）
  if (process.env.NODE_ENV === 'development') {
    console.log('[API Response]', {
      method: config.method?.toUpperCase(),
      url: config.url,
      status,
      data
    });
  }

  // 统一响应格式转换
  // 如果后端返回的数据已经是标准格式，直接返回
  if (data && typeof data === 'object' && 'success' in data) {
    return response;
  }

  // 否则包装成标准格式
  response.data = {
    success: true,
    data: data,
    message: '操作成功',
    timestamp: new Date().toISOString()
  };

  return response;
}

/**
 * 响应错误拦截器
 * 在请求失败或响应错误时执行
 *
 * @param {Object} error - axios错误对象
 * @returns {Promise} - 拒绝的Promise
 */
async function responseErrorInterceptor(error) {
  const { config, response } = error;

  // 记录错误日志
  console.error('[API Error]', {
    method: config?.method?.toUpperCase(),
    url: config?.url,
    status: response?.status,
    message: error.message,
    data: response?.data
  });

  // 处理特殊的HTTP状态码
  if (response) {
    switch (response.status) {
      case 401:
        // 认证失败，清除token并跳转到登录页
        await handleAuthenticationError();
        break;

      case 403:
        // 权限不足
        handlePermissionError();
        break;

      case 404:
        // 资源不存在
        handleNotFoundError(config);
        break;

      case 429:
        // 请求过于频繁
        handleRateLimitError();
        break;

      default:
        break;
    }
  }

  // 拒绝Promise，让外层的错误处理逻辑继续处理
  return Promise.reject(error);
}

/**
 * 获取认证token
 *
 * @returns {string|null} - token或null
 */
function getAuthToken() {
  try {
    // 从localStorage获取token
    const token = localStorage.getItem('authToken');
    return token;
  } catch (error) {
    console.error('获取token失败:', error);
    return null;
  }
}

/**
 * 处理认证错误（401）
 */
async function handleAuthenticationError() {
  // 清除本地token
  localStorage.removeItem('authToken');
  localStorage.removeItem('userInfo');

  // TODO: 根据实际需求决定是否跳转到登录页
  // 如果项目有认证功能，取消下面的注释
  // window.location.href = '/login';

  console.warn('认证失败，请重新登录');
}

/**
 * 处理权限错误（403）
 */
function handlePermissionError() {
  console.warn('权限不足，无法执行此操作');
  // TODO: 可以显示权限不足的提示或跳转到无权限页面
}

/**
 * 处理资源不存在错误（404）
 *
 * @param {Object} config - 请求配置
 */
function handleNotFoundError(config) {
  console.warn(`资源不存在: ${config?.url}`);
  // TODO: 可以记录404错误用于监控
}

/**
 * 处理频率限制错误（429）
 */
function handleRateLimitError() {
  console.warn('请求过于频繁，请稍后再试');
  // TODO: 可以显示频率限制的提示
}

export default {
  setupInterceptors,
  requestInterceptor,
  responseSuccessInterceptor,
  responseErrorInterceptor
};
