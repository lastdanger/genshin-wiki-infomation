/**
 * API 错误类
 *
 * 处理所有来自后端 API 的错误
 */

import { ErrorCode, ErrorSeverity, ErrorInfo, ErrorDetail, ApiErrorResponse } from './types';

/**
 * API 错误基类
 */
export class ApiError extends Error {
  public readonly code: ErrorCode;
  public readonly severity: ErrorSeverity;
  public readonly details?: ErrorDetail[] | Record<string, any>;
  public readonly timestamp: Date;
  public readonly requestId?: string;
  public readonly path?: string;
  public readonly statusCode?: number;

  constructor(
    message: string,
    code: ErrorCode,
    severity: ErrorSeverity = ErrorSeverity.MEDIUM,
    options?: {
      details?: ErrorDetail[] | Record<string, any>;
      requestId?: string;
      path?: string;
      statusCode?: number;
      originalError?: Error;
    }
  ) {
    super(message);
    this.name = 'ApiError';
    this.code = code;
    this.severity = severity;
    this.details = options?.details;
    this.requestId = options?.requestId;
    this.path = options?.path;
    this.statusCode = options?.statusCode;
    this.timestamp = new Date();

    // 保持正确的原型链
    Object.setPrototypeOf(this, ApiError.prototype);

    // 捕获堆栈跟踪
    if (Error.captureStackTrace) {
      Error.captureStackTrace(this, this.constructor);
    }
  }

  /**
   * 转换为 ErrorInfo 对象
   */
  toErrorInfo(): ErrorInfo {
    return {
      code: this.code,
      message: this.message,
      severity: this.severity,
      details: this.details,
      timestamp: this.timestamp,
      requestId: this.requestId,
      path: this.path,
      stack: this.stack,
    };
  }

  /**
   * 从 API 响应创建 ApiError
   */
  static fromApiResponse(response: ApiErrorResponse, statusCode: number): ApiError {
    const errorData = response.error;
    const code = this.mapErrorCodeFromApi(errorData.code);
    const severity = this.determineSeverity(statusCode, code);

    return new ApiError(errorData.message, code, severity, {
      details: errorData.details,
      requestId: errorData.request_id,
      path: errorData.path,
      statusCode,
    });
  }

  /**
   * 映射 API 错误代码到前端错误代码
   */
  private static mapErrorCodeFromApi(apiCode: string): ErrorCode {
    const codeMap: Record<string, ErrorCode> = {
      VALIDATION_ERROR: ErrorCode.VALIDATION_ERROR,
      NOT_FOUND: ErrorCode.NOT_FOUND,
      UNAUTHORIZED: ErrorCode.UNAUTHORIZED,
      FORBIDDEN: ErrorCode.FORBIDDEN,
      CONFLICT: ErrorCode.CONFLICT,
      RATE_LIMIT_EXCEEDED: ErrorCode.RATE_LIMIT_EXCEEDED,
      INTERNAL_SERVER_ERROR: ErrorCode.INTERNAL_SERVER_ERROR,
      DATABASE_ERROR: ErrorCode.DATABASE_ERROR,
      EXTERNAL_API_ERROR: ErrorCode.EXTERNAL_API_ERROR,
      SERVICE_UNAVAILABLE: ErrorCode.SERVICE_UNAVAILABLE,
      BAD_REQUEST: ErrorCode.BAD_REQUEST,
    };

    return codeMap[apiCode] || ErrorCode.UNKNOWN_ERROR;
  }

  /**
   * 根据状态码和错误代码确定严重程度
   */
  private static determineSeverity(statusCode: number, code: ErrorCode): ErrorSeverity {
    // 5xx 错误通常是高严重性
    if (statusCode >= 500) {
      return ErrorSeverity.HIGH;
    }

    // 特定错误代码的严重性
    switch (code) {
      case ErrorCode.UNAUTHORIZED:
      case ErrorCode.FORBIDDEN:
        return ErrorSeverity.HIGH;
      case ErrorCode.VALIDATION_ERROR:
      case ErrorCode.NOT_FOUND:
        return ErrorSeverity.LOW;
      case ErrorCode.RATE_LIMIT_EXCEEDED:
      case ErrorCode.CONFLICT:
        return ErrorSeverity.MEDIUM;
      default:
        return ErrorSeverity.MEDIUM;
    }
  }
}

/**
 * 网络错误类
 */
export class NetworkError extends ApiError {
  constructor(message: string = '网络连接失败，请检查网络设置') {
    super(message, ErrorCode.NETWORK_ERROR, ErrorSeverity.HIGH);
    this.name = 'NetworkError';
    Object.setPrototypeOf(this, NetworkError.prototype);
  }
}

/**
 * 超时错误类
 */
export class TimeoutError extends ApiError {
  constructor(message: string = '请求超时，请重试') {
    super(message, ErrorCode.TIMEOUT_ERROR, ErrorSeverity.MEDIUM);
    this.name = 'TimeoutError';
    Object.setPrototypeOf(this, TimeoutError.prototype);
  }
}

/**
 * 验证错误类
 */
export class ValidationError extends ApiError {
  constructor(message: string, details?: ErrorDetail[]) {
    super(message, ErrorCode.VALIDATION_ERROR, ErrorSeverity.LOW, { details });
    this.name = 'ValidationError';
    Object.setPrototypeOf(this, ValidationError.prototype);
  }
}

/**
 * 未找到错误类
 */
export class NotFoundError extends ApiError {
  constructor(resource: string, message?: string) {
    const errorMessage = message || `请求的${resource}不存在`;
    super(errorMessage, ErrorCode.NOT_FOUND, ErrorSeverity.LOW);
    this.name = 'NotFoundError';
    Object.setPrototypeOf(this, NotFoundError.prototype);
  }
}

/**
 * 服务器错误类
 */
export class ServerError extends ApiError {
  constructor(message: string = '服务器错误，我们正在处理', details?: Record<string, any>) {
    super(message, ErrorCode.INTERNAL_SERVER_ERROR, ErrorSeverity.HIGH, { details });
    this.name = 'ServerError';
    Object.setPrototypeOf(this, ServerError.prototype);
  }
}

/**
 * 认证错误类
 */
export class AuthenticationError extends ApiError {
  constructor(message: string = '身份验证失败，请重新登录') {
    super(message, ErrorCode.UNAUTHORIZED, ErrorSeverity.HIGH);
    this.name = 'AuthenticationError';
    Object.setPrototypeOf(this, AuthenticationError.prototype);
  }
}
