/**
 * 错误类统一导出
 *
 * 提供错误类型的工厂方法和工具函数
 */
import NetworkError from './NetworkError';
import BusinessError from './BusinessError';
import SystemError from './SystemError';

/**
 * 根据HTTP响应创建对应的错误对象
 *
 * @param {Object} error - Axios错误对象
 * @param {Object} config - 请求配置
 * @returns {NetworkError|BusinessError|SystemError}
 */
export function createErrorFromResponse(error, config = {}) {
  // 网络错误（没有响应）
  if (!error.response) {
    return new NetworkError(
      error.message || '网络连接失败',
      error,
      config
    );
  }

  const { status, data } = error.response;

  // 业务错误（4xx）
  if (status >= 400 && status < 500) {
    return new BusinessError(
      data?.error?.message || data?.message || '请求失败',
      data?.error?.code || `HTTP_${status}`,
      status,
      data?.error?.details || data?.details,
      config
    );
  }

  // 系统错误（5xx）
  if (status >= 500) {
    return new SystemError(
      data?.error?.message || data?.message || '服务器错误',
      status,
      error,
      config
    );
  }

  // 未知错误
  return new SystemError(
    '未知错误',
    status || 500,
    error,
    config
  );
}

/**
 * 判断错误是否可重试
 *
 * @param {Error} error - 错误对象
 * @returns {boolean}
 */
export function isRetryableError(error) {
  return error instanceof NetworkError && error.retryable;
}

/**
 * 判断错误是否需要认证
 *
 * @param {Error} error - 错误对象
 * @returns {boolean}
 */
export function isAuthenticationError(error) {
  return error instanceof BusinessError && error.isAuthenticationError();
}

/**
 * 获取错误的用户提示消息
 *
 * @param {Error} error - 错误对象
 * @returns {string}
 */
export function getUserMessage(error) {
  if (error.getUserMessage && typeof error.getUserMessage === 'function') {
    return error.getUserMessage();
  }
  return error.message || '操作失败，请稍后重试';
}

/**
 * 获取错误详情（用于日志）
 *
 * @param {Error} error - 错误对象
 * @returns {Object}
 */
export function getErrorDetails(error) {
  if (error.getDetails && typeof error.getDetails === 'function') {
    return error.getDetails();
  }
  return {
    name: error.name,
    message: error.message,
    stack: error.stack
  };
}

export {
  NetworkError,
  BusinessError,
  SystemError
};

export default {
  NetworkError,
  BusinessError,
  SystemError,
  createErrorFromResponse,
  isRetryableError,
  isAuthenticationError,
  getUserMessage,
  getErrorDetails
};
