/**
 * 业务错误类
 *
 * 表示业务逻辑层面的错误，如参数验证失败、权限不足、资源不存在等
 * HTTP 4xx状态码对应的错误
 * 这类错误通常不需要自动重试，需要用户修正输入
 */
class BusinessError extends Error {
  constructor(message, code, statusCode, details = null, config = {}) {
    super(message);
    this.name = 'BusinessError';
    this.type = 'business';
    this.code = code; // 业务错误码，如 'VALIDATION_ERROR', 'NOT_FOUND'
    this.statusCode = statusCode; // HTTP状态码
    this.details = details; // 详细错误信息（如字段级验证错误）
    this.config = config;
    this.timestamp = new Date().toISOString();
    this.retryable = false; // 业务错误不可重试

    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, BusinessError);
    }
  }

  /**
   * 获取用户友好的错误消息
   */
  getUserMessage() {
    // 根据错误码返回中文提示
    const errorMessages = {
      'VALIDATION_ERROR': '请求参数验证失败，请检查输入',
      'AUTHENTICATION_ERROR': '认证失败，请重新登录',
      'PERMISSION_DENIED': '您没有权限执行此操作',
      'NOT_FOUND': '请求的资源不存在',
      'CONFLICT': '资源冲突，请刷新后重试',
      'RATE_LIMIT': '请求过于频繁，请稍后再试'
    };

    return errorMessages[this.code] || this.message || '请求失败，请稍后重试';
  }

  /**
   * 获取字段级错误详情
   */
  getFieldErrors() {
    if (this.details && typeof this.details === 'object') {
      return this.details;
    }
    return {};
  }

  /**
   * 获取错误详情（用于日志记录）
   */
  getDetails() {
    return {
      name: this.name,
      type: this.type,
      code: this.code,
      statusCode: this.statusCode,
      message: this.message,
      details: this.details,
      timestamp: this.timestamp,
      config: {
        url: this.config?.url,
        method: this.config?.method
      }
    };
  }

  /**
   * 判断是否为验证错误
   */
  isValidationError() {
    return this.code === 'VALIDATION_ERROR' || this.statusCode === 400;
  }

  /**
   * 判断是否为认证错误
   */
  isAuthenticationError() {
    return this.code === 'AUTHENTICATION_ERROR' || this.statusCode === 401;
  }

  /**
   * 判断是否为权限错误
   */
  isPermissionError() {
    return this.code === 'PERMISSION_DENIED' || this.statusCode === 403;
  }

  /**
   * 判断是否为资源不存在错误
   */
  isNotFoundError() {
    return this.code === 'NOT_FOUND' || this.statusCode === 404;
  }
}

export default BusinessError;
