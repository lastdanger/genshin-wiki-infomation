/**
 * 请求重试策略
 *
 * 实现指数退避算法的请求重试机制
 * 仅对网络错误进行重试，业务错误不重试
 */

/**
 * 默认重试配置
 */
const DEFAULT_RETRY_CONFIG = {
  maxRetries: 3, // 最大重试次数
  initialDelay: 1000, // 初始延迟（毫秒）
  maxDelay: 10000, // 最大延迟（毫秒）
  backoffFactor: 2, // 退避因子（每次重试延迟翻倍）
  retryCondition: (error) => {
    // 默认重试条件：网络错误
    return !error.response || error.code === 'ECONNABORTED';
  }
};

/**
 * 执行请求重试
 *
 * @param {Object} axiosInstance - axios实例
 * @param {Object} config - 请求配置
 * @param {Object} retryConfig - 重试配置
 * @returns {Promise<Object>} - axios响应
 */
export async function retryRequest(
  axiosInstance,
  config,
  retryConfig = {}
) {
  // 合并重试配置
  const finalConfig = {
    ...DEFAULT_RETRY_CONFIG,
    ...retryConfig
  };

  // 记录重试次数
  config.__retryCount = config.__retryCount || 0;

  // 执行重试
  for (let attempt = 1; attempt <= finalConfig.maxRetries; attempt++) {
    try {
      // 记录重试日志
      console.log(`[重试] 第 ${attempt}/${finalConfig.maxRetries} 次尝试:`, {
        url: config.url,
        method: config.method
      });

      // 发送请求
      const response = await axiosInstance.request(config);

      // 请求成功，返回响应
      console.log(`[重试成功] 第 ${attempt} 次尝试成功`);
      return response;
    } catch (error) {
      // 更新重试次数
      config.__retryCount = attempt;

      // 判断是否应该重试
      const shouldRetry =
        attempt < finalConfig.maxRetries &&
        finalConfig.retryCondition(error);

      if (!shouldRetry) {
        // 不应该重试，抛出错误
        console.error(`[重试失败] 已达到最大重试次数或不满足重试条件`);
        throw error;
      }

      // 计算延迟时间（指数退避）
      const delay = calculateDelay(
        attempt,
        finalConfig.initialDelay,
        finalConfig.maxDelay,
        finalConfig.backoffFactor
      );

      // 记录延迟信息
      console.log(`[重试延迟] ${delay}ms 后进行第 ${attempt + 1} 次尝试`);

      // 延迟后继续重试
      await sleep(delay);
    }
  }

  // 理论上不会执行到这里，因为循环中会返回或抛出错误
  throw new Error('重试失败');
}

/**
 * 计算重试延迟时间（指数退避算法）
 *
 * @param {number} attempt - 当前重试次数
 * @param {number} initialDelay - 初始延迟
 * @param {number} maxDelay - 最大延迟
 * @param {number} backoffFactor - 退避因子
 * @returns {number} - 延迟时间（毫秒）
 */
function calculateDelay(attempt, initialDelay, maxDelay, backoffFactor) {
  // 指数退避：delay = initialDelay * (backoffFactor ^ (attempt - 1))
  const exponentialDelay = initialDelay * Math.pow(backoffFactor, attempt - 1);

  // 添加随机抖动（避免惊群效应）
  const jitter = Math.random() * 0.3 * exponentialDelay;

  // 计算最终延迟（不超过最大延迟）
  const finalDelay = Math.min(exponentialDelay + jitter, maxDelay);

  return Math.round(finalDelay);
}

/**
 * 延迟函数
 *
 * @param {number} ms - 延迟时间（毫秒）
 * @returns {Promise<void>}
 */
function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 创建自定义重试策略
 *
 * @param {Object} config - 重试配置
 * @returns {Function} - 重试函数
 */
export function createRetryPolicy(config) {
  const mergedConfig = {
    ...DEFAULT_RETRY_CONFIG,
    ...config
  };

  return async (axiosInstance, requestConfig) => {
    return retryRequest(axiosInstance, requestConfig, mergedConfig);
  };
}

/**
 * 判断错误是否应该重试
 *
 * @param {Object} error - axios错误对象
 * @returns {boolean}
 */
export function shouldRetry(error) {
  // 网络错误（没有响应）
  if (!error.response) {
    return true;
  }

  // 超时错误
  if (error.code === 'ECONNABORTED') {
    return true;
  }

  // 某些5xx错误可以重试
  const status = error.response?.status;
  const retryableStatusCodes = [502, 503, 504];

  if (retryableStatusCodes.includes(status)) {
    return true;
  }

  // 其他情况不重试
  return false;
}

/**
 * 重试配置预设
 */
export const RETRY_PRESETS = {
  // 快速重试（适合轻量级请求）
  FAST: {
    maxRetries: 2,
    initialDelay: 500,
    maxDelay: 2000,
    backoffFactor: 2
  },

  // 标准重试（默认）
  STANDARD: DEFAULT_RETRY_CONFIG,

  // 持久重试（适合重要请求）
  PERSISTENT: {
    maxRetries: 5,
    initialDelay: 2000,
    maxDelay: 30000,
    backoffFactor: 2
  },

  // 无重试
  NONE: {
    maxRetries: 0
  }
};

export default {
  retryRequest,
  createRetryPolicy,
  shouldRetry,
  RETRY_PRESETS
};
