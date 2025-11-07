/**
 * 系统错误类
 *
 * 表示系统层面的错误，如服务器内部错误、未知错误等
 * HTTP 5xx状态码对应的错误
 * 这类错误需要记录日志但不应向用户暴露技术细节
 */
class SystemError extends Error {
  constructor(message, statusCode, originalError = null, config = {}) {
    super(message);
    this.name = 'SystemError';
    this.type = 'system';
    this.statusCode = statusCode; // HTTP状态码
    this.originalError = originalError;
    this.config = config;
    this.timestamp = new Date().toISOString();
    this.retryable = false; // 系统错误一般不自动重试

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, SystemError);
    }
  }

  /**
   * 获取用户友好的错误消息（不暴露技术细节）
   */
  getUserMessage() {
    const errorMessages = {
      500: '服务器内部错误，请稍后重试',
      502: '网关错误，服务暂时不可用',
      503: '服务暂时不可用，请稍后重试',
      504: '网关超时，请稍后重试'
    };

    return errorMessages[this.statusCode] || '系统繁忙，请稍后重试';
  }

  /**
   * 获取错误详情（用于日志记录和开发调试）
   */
  getDetails() {
    return {
      name: this.name,
      type: this.type,
      statusCode: this.statusCode,
      message: this.message,
      timestamp: this.timestamp,
      config: {
        url: this.config?.url,
        method: this.config?.method,
        headers: this.config?.headers
      },
      originalError: {
        message: this.originalError?.message,
        stack: this.originalError?.stack
      },
      userAgent: navigator?.userAgent,
      url: window?.location?.href
    };
  }

  /**
   * 判断是否为服务器内部错误
   */
  isInternalServerError() {
    return this.statusCode === 500;
  }

  /**
   * 判断是否为网关错误
   */
  isGatewayError() {
    return this.statusCode === 502 || this.statusCode === 504;
  }

  /**
   * 判断是否为服务不可用
   */
  isServiceUnavailable() {
    return this.statusCode === 503;
  }
}

export default SystemError;
