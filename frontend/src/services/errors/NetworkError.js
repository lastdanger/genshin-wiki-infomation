/**
 * 网络错误类
 *
 * 表示网络层面的错误，如连接失败、超时、DNS解析失败等
 * 这类错误通常需要自动重试
 */
class NetworkError extends Error {
  constructor(message, originalError = null, config = {}) {
    super(message);
    this.name = 'NetworkError';
    this.type = 'network';
    this.originalError = originalError;
    this.config = config;
    this.timestamp = new Date().toISOString();
    this.retryable = true; // 网络错误可重试

    // 捕获堆栈信息
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, NetworkError);
    }
  }

  /**
   * 获取用户友好的错误消息
   */
  getUserMessage() {
    return this.message || '网络连接失败，请检查网络设置';
  }

  /**
   * 获取错误详情（用于日志记录）
   */
  getDetails() {
    return {
      name: this.name,
      type: this.type,
      message: this.message,
      timestamp: this.timestamp,
      config: {
        url: this.config?.url,
        method: this.config?.method,
        timeout: this.config?.timeout
      },
      originalError: this.originalError?.message
    };
  }

  /**
   * 判断是否为超时错误
   */
  isTimeout() {
    return this.originalError?.code === 'ECONNABORTED' ||
           this.message.includes('timeout');
  }

  /**
   * 判断是否为连接失败
   */
  isConnectionFailed() {
    return this.originalError?.code === 'ECONNREFUSED' ||
           this.originalError?.code === 'ENETUNREACH' ||
           this.message.includes('Network Error');
  }
}

export default NetworkError;
