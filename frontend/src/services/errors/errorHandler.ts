/**
 * 错误处理工具
 *
 * 提供统一的错误处理、日志记录和用户提示功能
 */

import { AxiosError } from 'axios';
import {
  ApiError,
  NetworkError,
  TimeoutError,
  ServerError,
  NotFoundError,
  ValidationError,
  AuthenticationError,
} from './ApiError';
import { ErrorCode, ErrorSeverity, ErrorHandlerOptions, ApiErrorResponse } from './types';

/**
 * 用户友好的错误消息映射
 */
const USER_FRIENDLY_MESSAGES: Record<ErrorCode, string> = {
  [ErrorCode.NETWORK_ERROR]: '网络连接失败，请检查您的网络设置',
  [ErrorCode.TIMEOUT_ERROR]: '请求超时，请稍后重试',
  [ErrorCode.CONNECTION_ERROR]: '无法连接到服务器',
  [ErrorCode.BAD_REQUEST]: '请求参数错误，请检查输入',
  [ErrorCode.UNAUTHORIZED]: '身份验证失败，请重新登录',
  [ErrorCode.FORBIDDEN]: '您没有权限执行此操作',
  [ErrorCode.NOT_FOUND]: '请求的资源不存在',
  [ErrorCode.CONFLICT]: '操作冲突，请刷新页面后重试',
  [ErrorCode.VALIDATION_ERROR]: '输入数据验证失败',
  [ErrorCode.RATE_LIMIT_EXCEEDED]: '请求过于频繁，请稍后再试',
  [ErrorCode.INTERNAL_SERVER_ERROR]: '服务器错误，我们正在处理',
  [ErrorCode.DATABASE_ERROR]: '数据库暂时不可用，请稍后重试',
  [ErrorCode.EXTERNAL_API_ERROR]: '外部服务暂时不可用',
  [ErrorCode.SERVICE_UNAVAILABLE]: '服务暂时不可用，请稍后重试',
  [ErrorCode.RENDER_ERROR]: '页面渲染出错',
  [ErrorCode.UNKNOWN_ERROR]: '未知错误，请刷新页面重试',
};

/**
 * 错误处理器类
 */
export class ErrorHandler {
  /**
   * 处理 Axios 错误
   */
  static handleAxiosError(error: AxiosError): ApiError {
    // 网络错误（没有响应）
    if (!error.response) {
      if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
        return new TimeoutError();
      }
      return new NetworkError();
    }

    const { status, data } = error.response;

    // 尝试解析 API 错误响应
    if (this.isApiErrorResponse(data)) {
      return ApiError.fromApiResponse(data as ApiErrorResponse, status);
    }

    // 根据状态码创建特定错误
    return this.createErrorFromStatus(status, error);
  }

  /**
   * 检查是否是 API 错误响应格式
   */
  private static isApiErrorResponse(data: any): data is ApiErrorResponse {
    return (
      data &&
      typeof data === 'object' &&
      data.success === false &&
      data.error &&
      typeof data.error.code === 'string' &&
      typeof data.error.message === 'string'
    );
  }

  /**
   * 根据 HTTP 状态码创建错误
   */
  private static createErrorFromStatus(status: number, error: AxiosError): ApiError {
    const message = typeof error.response?.data === 'string'
      ? error.response.data
      : error.message;

    switch (status) {
      case 400:
        return new ApiError('请求参数错误', ErrorCode.BAD_REQUEST, ErrorSeverity.LOW);
      case 401:
        return new AuthenticationError();
      case 403:
        return new ApiError('权限不足', ErrorCode.FORBIDDEN, ErrorSeverity.MEDIUM);
      case 404:
        return new NotFoundError('资源');
      case 409:
        return new ApiError('操作冲突', ErrorCode.CONFLICT, ErrorSeverity.MEDIUM);
      case 422:
        return new ValidationError('数据验证失败');
      case 429:
        return new ApiError(
          '请求频率超限',
          ErrorCode.RATE_LIMIT_EXCEEDED,
          ErrorSeverity.MEDIUM
        );
      case 500:
        return new ServerError();
      case 503:
        return new ApiError(
          '服务暂时不可用',
          ErrorCode.SERVICE_UNAVAILABLE,
          ErrorSeverity.HIGH
        );
      default:
        return new ApiError(
          message || '请求失败',
          ErrorCode.UNKNOWN_ERROR,
          ErrorSeverity.MEDIUM,
          { statusCode: status }
        );
    }
  }

  /**
   * 处理通用 JavaScript 错误
   */
  static handleGeneralError(error: Error): ApiError {
    return new ApiError(
      error.message || '发生未知错误',
      ErrorCode.UNKNOWN_ERROR,
      ErrorSeverity.MEDIUM,
      { originalError: error }
    );
  }

  /**
   * 获取用户友好的错误消息
   */
  static getUserFriendlyMessage(error: ApiError): string {
    // 如果错误已经有友好的消息，使用它
    if (error.message && !error.message.includes('Error')) {
      return error.message;
    }

    // 否则使用预定义的友好消息
    return USER_FRIENDLY_MESSAGES[error.code] || USER_FRIENDLY_MESSAGES[ErrorCode.UNKNOWN_ERROR];
  }

  /**
   * 记录错误到控制台
   */
  static logError(error: ApiError | Error, context?: string): void {
    const timestamp = new Date().toISOString();
    const prefix = context ? `[${context}]` : '[Error]';

    if (error instanceof ApiError) {
      console.error(`${prefix} ${timestamp}`, {
        code: error.code,
        message: error.message,
        severity: error.severity,
        details: error.details,
        path: error.path,
        requestId: error.requestId,
        stack: error.stack,
      });
    } else {
      console.error(`${prefix} ${timestamp}`, error);
    }
  }

  /**
   * 报告错误到监控服务（占位符，可以集成 Sentry 等服务）
   */
  static reportError(error: ApiError | Error, context?: Record<string, any>): void {
    // TODO: 集成错误监控服务（如 Sentry, LogRocket 等）
    if (process.env.NODE_ENV === 'production') {
      // 示例：Sentry.captureException(error, { extra: context });
      console.warn('Error reporting not implemented yet');
    }
  }

  /**
   * 处理错误（统一入口）
   */
  static handle(
    error: Error | AxiosError | ApiError,
    options: ErrorHandlerOptions = {}
  ): ApiError {
    let apiError: ApiError;

    // 转换为 ApiError
    if (error instanceof ApiError) {
      apiError = error;
    } else if ((error as AxiosError).isAxiosError) {
      apiError = this.handleAxiosError(error as AxiosError);
    } else {
      apiError = this.handleGeneralError(error as Error);
    }

    // 应用选项
    if (options.severity) {
      apiError = new ApiError(apiError.message, apiError.code, options.severity, {
        details: apiError.details,
        requestId: apiError.requestId,
        path: apiError.path,
        statusCode: apiError.statusCode,
      });
    }

    // 记录到控制台
    if (options.logToConsole !== false) {
      this.logError(apiError);
    }

    // 报告到监控服务
    if (options.reportToService) {
      this.reportError(apiError);
    }

    return apiError;
  }

  /**
   * 判断错误是否可以重试
   */
  static isRetryable(error: ApiError): boolean {
    const retryableCodes = [
      ErrorCode.NETWORK_ERROR,
      ErrorCode.TIMEOUT_ERROR,
      ErrorCode.SERVICE_UNAVAILABLE,
      ErrorCode.INTERNAL_SERVER_ERROR,
    ];

    return retryableCodes.includes(error.code);
  }

  /**
   * 判断是否需要重新登录
   */
  static requiresReauthentication(error: ApiError): boolean {
    return error.code === ErrorCode.UNAUTHORIZED;
  }
}

/**
 * 导出便捷函数
 */
export const handleError = ErrorHandler.handle.bind(ErrorHandler);
export const getUserFriendlyMessage = ErrorHandler.getUserFriendlyMessage.bind(ErrorHandler);
export const isRetryable = ErrorHandler.isRetryable.bind(ErrorHandler);
export const requiresReauthentication = ErrorHandler.requiresReauthentication.bind(ErrorHandler);
