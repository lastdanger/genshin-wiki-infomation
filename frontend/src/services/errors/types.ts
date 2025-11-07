/**
 * 错误类型定义
 *
 * 定义前端应用中所有可能的错误类型和错误代码
 */

/**
 * 错误代码枚举
 */
export enum ErrorCode {
  // 网络错误
  NETWORK_ERROR = 'NETWORK_ERROR',
  TIMEOUT_ERROR = 'TIMEOUT_ERROR',
  CONNECTION_ERROR = 'CONNECTION_ERROR',

  // 客户端错误 (4xx)
  BAD_REQUEST = 'BAD_REQUEST',
  UNAUTHORIZED = 'UNAUTHORIZED',
  FORBIDDEN = 'FORBIDDEN',
  NOT_FOUND = 'NOT_FOUND',
  CONFLICT = 'CONFLICT',
  VALIDATION_ERROR = 'VALIDATION_ERROR',
  RATE_LIMIT_EXCEEDED = 'RATE_LIMIT_EXCEEDED',

  // 服务器错误 (5xx)
  INTERNAL_SERVER_ERROR = 'INTERNAL_SERVER_ERROR',
  DATABASE_ERROR = 'DATABASE_ERROR',
  EXTERNAL_API_ERROR = 'EXTERNAL_API_ERROR',
  SERVICE_UNAVAILABLE = 'SERVICE_UNAVAILABLE',

  // 应用错误
  RENDER_ERROR = 'RENDER_ERROR',
  UNKNOWN_ERROR = 'UNKNOWN_ERROR',
}

/**
 * 错误严重程度
 */
export enum ErrorSeverity {
  LOW = 'low',
  MEDIUM = 'medium',
  HIGH = 'high',
  CRITICAL = 'critical',
}

/**
 * 错误详情接口
 */
export interface ErrorDetail {
  field?: string;
  message: string;
  type?: string;
  context?: Record<string, any>;
}

/**
 * API 错误响应接口
 */
export interface ApiErrorResponse {
  success: false;
  error: {
    code: string;
    message: string;
    details?: ErrorDetail[] | Record<string, any>;
    timestamp: string;
    path: string;
    request_id?: string;
  };
}

/**
 * 错误信息接口
 */
export interface ErrorInfo {
  code: ErrorCode;
  message: string;
  originalError?: Error;
  details?: ErrorDetail[] | Record<string, any>;
  severity: ErrorSeverity;
  timestamp: Date;
  stack?: string;
  requestId?: string;
  path?: string;
}

/**
 * 错误处理选项
 */
export interface ErrorHandlerOptions {
  showNotification?: boolean;
  notificationMessage?: string;
  logToConsole?: boolean;
  reportToService?: boolean;
  severity?: ErrorSeverity;
}
